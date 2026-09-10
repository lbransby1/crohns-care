# Crohns Care

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
