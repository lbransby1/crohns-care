"""Score extracted HBI fields against gold labels."""

from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from app.schemas import DailySymptomRecord
from eval.gold import GoldDay


def canon_comp(name: str) -> str:
    text = (name or "").lower().replace(" ulcers", " ulcer")
    text = text.replace("left knee swollen", "knee swelling")
    if "ulcer" in text or "canker" in text:
        return "mouth ulcer"
    if "swell" in text or "swollen" in text:
        return "knee swelling"
    if "arthralgia" in text or "joint" in text or "knee" in text:
        return "arthralgia"
    return text.strip()


def gold_hbi(record: DailySymptomRecord) -> int:
    return (
        record.general_wellbeing
        + record.abdominal_pain
        + record.liquid_stool_count
        + len(record.complications)
    )


def score_pairs(pairs: Iterable[tuple[GoldDay, DailySymptomRecord]]) -> dict:
    buckets: dict[str, list] = defaultdict(list)
    overall: list[dict] = []
    for gold, pred in pairs:
        row = _row(gold, pred)
        buckets[gold.style].append(row)
        overall.append(row)
    summary = {"overall": _aggregate(overall, "overall")}
    for style, rows in buckets.items():
        summary[style] = _aggregate(rows, style)
    return summary


def _row(gold: GoldDay, pred: DailySymptomRecord) -> dict:
    g = gold.record
    g_comps = {canon_comp(c) for c in g.complications}
    p_comps = {canon_comp(c) for c in pred.complications if canon_comp(c)}
    return {
        "style": gold.style,
        "formed": gold.formed_stool,
        "wb_ok": int(g.general_wellbeing == pred.general_wellbeing),
        "wb_abs": abs(g.general_wellbeing - pred.general_wellbeing),
        "pain_ok": int(g.abdominal_pain == pred.abdominal_pain),
        "pain_abs": abs(g.abdominal_pain - pred.abdominal_pain),
        "liq_ok": int(g.liquid_stool_count == pred.liquid_stool_count),
        "liq_abs": abs(g.liquid_stool_count - pred.liquid_stool_count),
        "liq_fp_formed": int(gold.formed_stool and pred.liquid_stool_count > 0),
        "hbi_ok": int(gold_hbi(g) == gold_hbi(pred)),
        "hbi_abs": abs(gold_hbi(g) - gold_hbi(pred)),
        "adh_ok": int(g.medication_adherence == pred.medication_adherence),
        "comp_tp": len(g_comps & p_comps),
        "comp_pred": len(p_comps),
        "comp_gold": len(g_comps),
        "day_ok": int(pred.day == g.day),
    }


def _aggregate(rows: list[dict], slice_name: str) -> dict:
    n = len(rows)
    if n == 0:
        return {"slice": slice_name, "n": 0}
    tp = sum(r["comp_tp"] for r in rows)
    pred_n = sum(r["comp_pred"] for r in rows)
    gold_n = sum(r["comp_gold"] for r in rows)
    n_formed = sum(1 for r in rows if r["formed"])
    fp_formed = sum(r["liq_fp_formed"] for r in rows)
    return {
        "slice": slice_name,
        "n": n,
        "wb_acc": _mean(r["wb_ok"] for r in rows),
        "wb_mae": _mean(r["wb_abs"] for r in rows),
        "pain_acc": _mean(r["pain_ok"] for r in rows),
        "pain_mae": _mean(r["pain_abs"] for r in rows),
        "liq_acc": _mean(r["liq_ok"] for r in rows),
        "liq_mae": _mean(r["liq_abs"] for r in rows),
        "liq_fp_formed": (fp_formed / n_formed) if n_formed else 0.0,
        "hbi_acc": _mean(r["hbi_ok"] for r in rows),
        "hbi_mae": _mean(r["hbi_abs"] for r in rows),
        "hbi_within_1": _mean(r["hbi_abs"] <= 1 for r in rows),
        "adh_acc": _mean(r["adh_ok"] for r in rows),
        "comp_p": (tp / pred_n) if pred_n else 1.0,
        "comp_r": (tp / gold_n) if gold_n else 1.0,
        "day_acc": _mean(r["day_ok"] for r in rows),
    }


def _mean(values: Iterable) -> float:
    seq = list(values)
    if not seq:
        return 0.0
    return sum(float(v) for v in seq) / len(seq)


def format_table(summary: dict) -> str:
    headers = [
        "slice",
        "n",
        "wb_acc",
        "pain_acc",
        "liq_acc",
        "liq_mae",
        "liq_fp",
        "hbi_acc",
        "hbi_mae",
        "hbi±1",
        "adh_acc",
        "comp_p",
        "comp_r",
        "day_acc",
    ]
    order = ["overall", "clinic", "informal", "terse", "bristol_ambiguous"]
    lines = ["  ".join(f"{h:>20}" if h == "slice" else f"{h:>8}" for h in headers)]
    for key in order:
        row = summary.get(key)
        if not row or not row.get("n"):
            continue
        values = [
            f"{row['slice']:>20}",
            f"{row['n']:>8}",
            f"{row['wb_acc']:>8.3f}",
            f"{row['pain_acc']:>8.3f}",
            f"{row['liq_acc']:>8.3f}",
            f"{row['liq_mae']:>8.3f}",
            f"{row['liq_fp_formed']:>8.3f}",
            f"{row['hbi_acc']:>8.3f}",
            f"{row['hbi_mae']:>8.3f}",
            f"{row['hbi_within_1']:>8.3f}",
            f"{row['adh_acc']:>8.3f}",
            f"{row['comp_p']:>8.3f}",
            f"{row['comp_r']:>8.3f}",
            f"{row['day_acc']:>8.3f}",
        ]
        lines.append("  ".join(values))
    return "\n".join(lines)
