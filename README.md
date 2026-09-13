# Crohn's Care

This is not a medical diagnostics tool. It is non-diagnostic decision support for demonstration. It does not diagnose Crohn’s disease, assess flare risk, or replace a qualified clinician. Do not use it for treatment decisions.

## The problem

Crohn’s symptoms are often recorded as messy daily notes: slang, skipped days, one-word entries, and out-of-order fragments. That makes it hard for patients to communicate how they have actually been, and hard for a clinician to scan a diary into a clear trajectory.

## How it works

Choose a synthetic diary or paste your own. A language model extracts Harvey-Bradshaw Index fields from each day (wellbeing, pain, liquid stools, extra-intestinal signs, medication adherence). Python then scores HBI, baseline vs current windows, and adherence — the model does not do the arithmetic. A short outpatient brief and PDF are generated from those metrics plus retrieved log excerpts.

## RAG

Each run builds an ephemeral Chroma index of that diary only. The synthesizer does not read every day in full. It retrieves a few temporally labelled chunks for dietary triggers, complications, medication mentions, and stool pattern, then writes the narrative from those spans plus the deterministic stats.

## Guardrails

- Structured extraction via a Pydantic schema, not free-form diagnosis.
- Only Bristol 6–7 stools count toward liquid stool score.
- Dietary links are only flagged inside a 24–48 hour window, and only if they appear in retrieved notes.
- The brief is non-prescriptive: no drug, diet, or referral advice.
- Diaries stay in memory for the request; collections are not shared across patients.

## Project structure

```
app/
  main.py                 FastAPI routes, static UI, JSON error handling
  config.py               Cerebras settings and diary limits
  schemas.py              Pydantic models for extraction and the analyze response
  data/sample_logs.py     Synthetic diaries, including messy and 90-day cases
  services/
    parser.py             Line / CSV / JSON diary parsing
    extraction.py         Instructor + Cerebras batch HBI extraction
    analytics.py          Deterministic HBI, windows, adherence, clinical tier
    rag.py                Per-request Chroma index and temporal retrieval
    synthesis.py          Grounded outpatient brief
    charts.py             HBI trajectory (matplotlib)
    pdf.py                One-page ReportLab brief
    pipeline.py           Orchestration and in-memory PDF store
  static/                 HTML / CSS / JS frontend
eval/                     Label-first synthetic benchmark
notebooks/                Original Colab PDF-generation demo
```

Pipeline: parse logs → extract HBI fields in 30-day chunks → score in Python → retrieve Chroma context → synthesise brief → chart + PDF.

The UI in `app/static/` is a single page (no frontend build). Presets live in `sample_logs.py`; messy cases keep a `raw` diary so blank lines and comments hit the parser the same way an upload would.

## Run locally

Set `CEREBRAS_API_KEY` in `.env` (see `.env.example`). Default model is `qwen-3.8-27b`.

```bash
cp .env.example .env

docker compose up --build
```

Open http://localhost:8000

Without Docker:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API

- `GET /health`
- `GET /api/presets`
- `GET /api/presets/{id}`
- `POST /api/analyze` with `{ "preset_id": "flare-14" }` or `{ "text": "Day 1: ..." }`
- `POST /api/analyze/upload` multipart file
- `GET /api/reports/{id}/pdf`

## Evaluation

Gold HBI labels are sampled first, then a note is rendered from them. Informal and terse notes sample independent paraphrases per field, so the extractor cannot win by memorising a few templates. Extraction is scored against those labels, not against the UI presets. The prompt stays at schema / HBI / Bristol level (no slang lexicon). This is a synthetic benchmark, not clinician-labelled real diaries.

Offline (no API key):

```bash
python -m unittest eval.test_analytics eval.test_parser eval.test_gold eval.test_guardrails eval.test_rag
```

Extraction benchmark (needs `CEREBRAS_API_KEY`):

```bash
python -m eval.run_extraction --n 140
```

Writes `eval/results.json`. Latest run: `qwen-3.8-27b`, 140 days, 11 diary batches.

### Extraction vs gold labels

| Slice | n | Wellbeing | Pain | Liquid | HBI exact | HBI ±1 | Adherence | Comp. P | Comp. R |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Overall | 140 | 0.850 | 0.879 | 1.000 | 0.771 | 0.957 | 1.000 | 0.867 | 0.852 |
| Clinic | 49 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.889 | 0.889 |
| Informal | 35 | 0.543 | 0.714 | 1.000 | 0.400 | 0.857 | 1.000 | 0.700 | 0.636 |
| Terse | 28 | 0.821 | 0.750 | 1.000 | 0.607 | 0.964 | 1.000 | 0.600 | 0.600 |
| Bristol-ambiguous | 28 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |

Day alignment was 1.000 on every slice. Formed-stool liquid false positives were 0. Clinic and Bristol-ambiguous are the production-like notes; informal (slang diary) and terse (telegraphic fragments) are the generalization slices.

### Diary-level and RAG

| Metric | Value |
| --- | ---: |
| Clinical tier accuracy | 0.909 |
| HBI trend-sign accuracy | 0.818 |
| Current-window HBI MAE | 0.245 |
| Diaries | 11 |
| Planted-span RAG recall@3 | 1.000 |

Tier is the activity bucket from current-window mean HBI (remission / mild / moderate-severe). Trend-sign is whether baseline→current HBI moved up, down, or stayed flat. RAG recall@3 is whether planted spans for diet, medication, complications, and stool pattern appear in the top-3 retrieved chunks.

