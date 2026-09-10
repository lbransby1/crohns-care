import csv
import io
import json
import re

from app.config import MAX_LOG_CHARS, MAX_LOG_DAYS

DAY_PREFIX = re.compile(r"^(?:day\s*)?(\d+)\s*[:.\-]\s*", re.IGNORECASE)
CSV_NOTE_HEADERS = {"note", "notes", "log", "logs", "text", "entry", "raw"}


def parse_log_document(raw: str) -> list[str]:
    text = (raw or "").strip()
    if not text:
        raise ValueError("No log text provided.")

    if text[0] in "{[":
        try:
            return _from_json(json.loads(text))
        except json.JSONDecodeError:
            pass

    if _looks_like_csv(text):
        parsed = _from_csv(text)
        if parsed:
            return _validate(parsed)

    return _validate(_from_lines(text))


def _from_json(data) -> list[str]:
    if isinstance(data, dict):
        for key in ("logs", "notes", "entries", "days"):
            if key in data:
                data = data[key]
                break
        else:
            raise ValueError("JSON object must contain a logs, notes, or entries array.")

    if not isinstance(data, list) or not data:
        raise ValueError("JSON must be a non-empty list of daily notes.")

    logs = []
    for item in data:
        if isinstance(item, str):
            logs.append(item)
        elif isinstance(item, dict):
            note = item.get("note") or item.get("text") or item.get("log") or item.get("raw")
            if not note:
                raise ValueError("Each JSON object needs a note/text/log field.")
            logs.append(str(note))
        else:
            raise ValueError("Unsupported JSON log item.")
    return _validate(logs)


def _looks_like_csv(text: str) -> bool:
    first = text.splitlines()[0]
    return "," in first and any(h in first.lower() for h in CSV_NOTE_HEADERS | {"day", "date"})


def _from_csv(text: str) -> list[str]:
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        return []
    fields = [f.strip() for f in reader.fieldnames]
    note_field = next((f for f in fields if f.lower() in CSV_NOTE_HEADERS), None)
    if note_field is None and len(fields) >= 2:
        note_field = fields[1]
    elif note_field is None:
        note_field = fields[0]

    rows = []
    for row in reader:
        value = (row.get(note_field) or "").strip()
        if value:
            rows.append(value)
    return rows


def _from_lines(text: str) -> list[str]:
    logs = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        line = DAY_PREFIX.sub("", line).strip()
        if line:
            logs.append(line)
    return logs


def _validate(logs: list[str]) -> list[str]:
    cleaned = []
    for i, log in enumerate(logs, start=1):
        note = " ".join(str(log).split())
        if not note:
            continue
        if len(note) > MAX_LOG_CHARS:
            raise ValueError(f"Day {i} exceeds {MAX_LOG_CHARS} characters.")
        cleaned.append(note)
    if not cleaned:
        raise ValueError("No daily notes found.")
    if len(cleaned) > MAX_LOG_DAYS:
        raise ValueError(f"Please keep logs to {MAX_LOG_DAYS} days or fewer.")
    return cleaned
