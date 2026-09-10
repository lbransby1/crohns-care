import asyncio
import logging
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import CEREBRAS_API_KEY, CEREBRAS_MODEL, MAX_UPLOAD_BYTES
from app.data.sample_logs import get_preset, preset_summaries
from app.schemas import AnalyzeRequest
from app.services.pipeline import get_pdf, resolve_logs, run_analysis

logger = logging.getLogger("hbi_brief")

STATIC_DIR = Path(__file__).resolve().parent / "static"

app = FastAPI(
    title="Crohns Care",
    description="Harvey-Bradshaw clinical briefs from Crohn's daily logs.",
    version="1.0.0",
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, (HTTPException, StarletteHTTPException)):
        return await http_exception_handler(request, exc)
    if isinstance(exc, RequestValidationError):
        return await request_validation_exception_handler(request, exc)
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    message = str(exc).strip() or exc.__class__.__name__
    return JSONResponse(status_code=500, content={"detail": message})


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model": CEREBRAS_MODEL,
        "cerebras_configured": bool(CEREBRAS_API_KEY),
    }


@app.get("/", response_class=HTMLResponse)
def index():
    return (STATIC_DIR / "index.html").read_text(encoding="utf-8")


@app.get("/api/presets")
def list_presets():
    return {"presets": preset_summaries()}


@app.get("/api/presets/{preset_id}")
def preset_detail(preset_id: str):
    preset = get_preset(preset_id)
    if not preset:
        raise HTTPException(status_code=404, detail="Unknown preset.")
    return preset


@app.post("/api/analyze")
async def analyze(body: AnalyzeRequest):
    if not CEREBRAS_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="CEREBRAS_API_KEY is not configured on this server.",
        )
    try:
        logs, label = resolve_logs(body.preset_id, body.logs, body.text)
        return await asyncio.to_thread(run_analysis, logs, label)
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Analyze failed")
        raise HTTPException(status_code=502, detail=str(exc) or exc.__class__.__name__) from exc


@app.post("/api/analyze/upload")
async def analyze_upload(file: UploadFile = File(...)):
    if not CEREBRAS_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="CEREBRAS_API_KEY is not configured on this server.",
        )
    blob = await file.read()
    if len(blob) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=400, detail="File is larger than 1 MB.")
    try:
        text = blob.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail="Please upload a UTF-8 text, CSV, or JSON file.") from exc
    try:
        logs, label = resolve_logs(None, None, text)
        return await asyncio.to_thread(run_analysis, logs, f"Uploaded · {file.filename or 'diary'}")
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Upload analyze failed")
        raise HTTPException(status_code=502, detail=str(exc) or exc.__class__.__name__) from exc


@app.get("/api/reports/{report_id}/pdf")
def download_pdf(report_id: str):
    pdf_bytes = get_pdf(report_id)
    if not pdf_bytes:
        raise HTTPException(
            status_code=404,
            detail="Report expired or was not found. Generate the brief again.",
        )
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="HBI_Clinical_Brief.pdf"'},
    )
