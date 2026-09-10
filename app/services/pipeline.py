import base64
import uuid
from collections import OrderedDict
from threading import RLock

from app.data.sample_logs import get_preset
from app.schemas import AnalyzeResponse
from app.services.analytics import build_history, compute_stats
from app.services.charts import build_hbi_chart
from app.services.extraction import extract_all_symptoms_batch
from app.services.parser import parse_log_document
from app.services.pdf import compile_clinical_pdf
from app.services.rag import retrieve_context
from app.services.synthesis import synthesize_brief

_STORE_LIMIT = 40
_lock = RLock()
_reports: OrderedDict[str, dict] = OrderedDict()


def resolve_logs(preset_id: str | None, logs: list[str] | None, text: str | None) -> tuple[list[str], str]:
    if preset_id:
        preset = get_preset(preset_id)
        if not preset:
            raise ValueError(f"Unknown preset: {preset_id}")
        return preset["logs"], preset["title"]
    if logs:
        cleaned = parse_log_document("\n".join(logs))
        return cleaned, "Uploaded diary"
    if text:
        return parse_log_document(text), "Uploaded diary"
    raise ValueError("Provide a preset_id, logs array, or diary text.")


def run_analysis(logs: list[str], source_label: str) -> AnalyzeResponse:
    with _lock:
        return _run_analysis_locked(logs, source_label)


def _run_analysis_locked(logs: list[str], source_label: str) -> AnalyzeResponse:
    records = extract_all_symptoms_batch(logs)
    history = build_history(logs, records)
    stats = compute_stats(history)
    rag_context = retrieve_context(history)
    summary = synthesize_brief(stats, rag_context)
    chart_png = build_hbi_chart(history)
    pdf_bytes = compile_clinical_pdf(stats, summary, chart_png)

    report_id = uuid.uuid4().hex
    payload = AnalyzeResponse(
        report_id=report_id,
        source_label=source_label,
        stats=stats,
        history=history,
        summary=summary,
        chart_png_b64=base64.b64encode(chart_png).decode("ascii"),
        rag_context=rag_context,
    )
    _store(report_id, pdf_bytes, payload)
    return payload


def get_pdf(report_id: str) -> bytes | None:
    with _lock:
        entry = _reports.get(report_id)
        if not entry:
            return None
        _reports.move_to_end(report_id)
        return entry["pdf"]


def _store(report_id: str, pdf_bytes: bytes, payload: AnalyzeResponse) -> None:
    with _lock:
        _reports[report_id] = {"pdf": pdf_bytes, "payload": payload}
        while len(_reports) > _STORE_LIMIT:
            _reports.popitem(last=False)
