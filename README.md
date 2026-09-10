# HBI Brief

Web app that turns Crohn's daily logs into a Harvey-Bradshaw outpatient brief. It uses the same stack as `notebooks/pdf-generation-demo.ipynb`: Cerebras (`qwen-3.8-27b`) + Instructor extraction, Chroma RAG, matplotlib trajectory, ReportLab PDF.

## Run locally

```bash
cp .env.example .env
# put your Cerebras key in .env

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

## Deploy on Railway

1. Push this repo to GitHub.
2. New project → Deploy from GitHub repo. Railway will pick up `Dockerfile` and `railway.toml`.
3. In the service variables, set `CEREBRAS_API_KEY`. Optionally override `CEREBRAS_MODEL` (default `qwen-3.8-27b`).
4. Generate a public domain under Settings → Networking.

Do not set `PORT` yourself. Railway injects it; the container binds `0.0.0.0:$PORT`.

## API

- `GET /health`
- `GET /api/presets`
- `POST /api/analyze` with `{ "preset_id": "flare-14" }` or `{ "text": "Day 1: ..." }`
- `GET /api/reports/{id}/pdf`
