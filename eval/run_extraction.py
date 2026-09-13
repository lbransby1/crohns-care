"""Run label-first extraction eval against Cerebras.

  python -m eval.run_extraction
  python -m eval.run_extraction --n 140 --batch-size 14
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from app.services.analytics import build_history, compute_stats
from app.services.extraction import extract_all_symptoms_batch
from eval.gold import pack_batches, sample_dataset
from eval.metrics import format_table, score_pairs
from eval.rag_eval import score_rag


def main() -> int:
    parser = argparse.ArgumentParser(description="Synthetic HBI extraction benchmark")
    parser.add_argument("--n", type=int, default=140, help="Number of labelled days (default 140)")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--batch-size", type=int, default=14)
    parser.add_argument("--out", type=Path, default=Path("eval/results.json"))
    parser.add_argument("--skip-rag", action="store_true")
    args = parser.parse_args()

    gold_days = sample_dataset(n=args.n, seed=args.seed)
    batches = pack_batches(gold_days, batch_size=args.batch_size)
    pairs = []
    diary_rows = []
    print(f"Evaluating {len(gold_days)} days in {len(batches)} batches...", file=sys.stderr)

    for i, batch in enumerate(batches, start=1):
        notes = [g.note for g in batch]
        print(f"  batch {i}/{len(batches)} ({batch[0].style}, {len(batch)} days)", file=sys.stderr)
        preds = extract_all_symptoms_batch(notes)
        if len(preds) != len(batch):
            print(f"    warn: got {len(preds)} records for {len(batch)} gold days", file=sys.stderr)
        for gold, pred in zip(batch, preds):
            pairs.append((gold, pred))
        gold_hist = build_history(notes, [g.record for g in batch])
        pred_hist = build_history(notes, preds[: len(batch)])
        gold_stats = compute_stats(gold_hist)
        pred_stats = compute_stats(pred_hist)
        diary_rows.append(
            {
                "style": batch[0].style,
                "n": len(batch),
                "tier_ok": gold_stats.clinical_tier == pred_stats.clinical_tier,
                "delta_sign_ok": _sign(gold_stats.hbi_trend_delta) == _sign(pred_stats.hbi_trend_delta),
                "current_hbi_abs": abs(gold_stats.current_hbi_avg - pred_stats.current_hbi_avg),
            }
        )

    summary = score_pairs(pairs)
    e2e = _e2e(diary_rows)
    rag = None if args.skip_rag else score_rag()

    payload = {
        "n_days": len(pairs),
        "n_batches": len(batches),
        "extraction": summary,
        "end_to_end": e2e,
        "rag": rag,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")

    print()
    print("Extraction vs gold labels")
    print(format_table(summary))
    print()
    print(
        "Diary-level  "
        f"tier_acc={e2e['tier_acc']:.3f}  "
        f"trend_sign_acc={e2e['delta_sign_acc']:.3f}  "
        f"current_hbi_mae={e2e['current_hbi_mae']:.3f}  "
        f"n_diaries={e2e['n']}"
    )
    if rag:
        print(
            "RAG planted-span recall@3 = "
            f"{rag['recall_at_3']:.3f}  found={rag['found']}"
        )
    print(f"Wrote {args.out}")
    return 0


def _sign(value: float) -> int:
    if value > 0.15:
        return 1
    if value < -0.15:
        return -1
    return 0


def _e2e(rows: list[dict]) -> dict:
    n = len(rows) or 1
    return {
        "n": len(rows),
        "tier_acc": sum(r["tier_ok"] for r in rows) / n,
        "delta_sign_acc": sum(r["delta_sign_ok"] for r in rows) / n,
        "current_hbi_mae": sum(r["current_hbi_abs"] for r in rows) / n,
    }


if __name__ == "__main__":
    raise SystemExit(main())
