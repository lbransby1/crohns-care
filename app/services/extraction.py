import time
from typing import List

import instructor
from openai import APIError, OpenAI, RateLimitError

from app.config import CEREBRAS_API_KEY, CEREBRAS_BASE_URL, CEREBRAS_MODEL
from app.schemas import BatchSymptoms, DailySymptomRecord

_instructor_client = None
_plain_client = None

EXTRA_BODY = {"reasoning_effort": "none"}


def _require_key() -> str:
    if not CEREBRAS_API_KEY:
        raise RuntimeError(
            "CEREBRAS_API_KEY is not set. Add it to your environment or Railway variables."
        )
    return CEREBRAS_API_KEY


def get_plain_client() -> OpenAI:
    global _plain_client
    if _plain_client is None:
        _plain_client = OpenAI(base_url=CEREBRAS_BASE_URL, api_key=_require_key())
    return _plain_client


def get_instructor_client():
    global _instructor_client
    if _instructor_client is None:
        _instructor_client = instructor.from_openai(
            get_plain_client(),
            mode=instructor.Mode.JSON,
        )
    return _instructor_client


def extract_all_symptoms_batch(logs: List[str], max_attempts: int = 5) -> List[DailySymptomRecord]:
    """Extract HBI fields in chunks so long diaries stay inside context."""
    chunk_size = 14
    all_records: List[DailySymptomRecord] = []
    for start in range(0, len(logs), chunk_size):
        chunk = logs[start : start + chunk_size]
        records = _extract_chunk(chunk, day_offset=start, max_attempts=max_attempts)
        all_records.extend(records)
    return all_records


def _extract_chunk(logs: List[str], day_offset: int, max_attempts: int) -> List[DailySymptomRecord]:
    formatted_input = "\n".join(f"Day {day_offset + i}: {note}" for i, note in enumerate(logs, 1))
    delay = 2.0
    client = get_instructor_client()

    last_error: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            res = client.chat.completions.create(
                model=CEREBRAS_MODEL,
                response_model=BatchSymptoms,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Extract daily Crohn's symptoms for each day according to the Harvey-Bradshaw Index. "
                            "Only count liquid or watery stools (Bristol 6-7). Solid stools = 0. "
                            "Keep the day numbers from the input. Return one record per day."
                        ),
                    },
                    {"role": "user", "content": formatted_input},
                ],
                temperature=0.0,
                extra_body=EXTRA_BODY,
            )
            records = sorted(res.records, key=lambda r: r.day)
            records = _remap_chunk_days(records, day_offset)
            if len(records) != len(logs):
                records = _align_records(records, logs, day_offset)
            return records
        except (RateLimitError, APIError, Exception) as exc:
            last_error = exc
            if attempt == max_attempts:
                break
            time.sleep(delay)
            delay *= 2.0

    raise RuntimeError(f"Symptom extraction failed after {max_attempts} attempts: {last_error}")


def _remap_chunk_days(records: List[DailySymptomRecord], day_offset: int) -> List[DailySymptomRecord]:
    """If the model numbered a later chunk from 1, shift it onto the global day index."""
    if not records or day_offset == 0:
        return records
    days = [r.day for r in records]
    if min(days) == 1:
        return [
            r.model_copy(update={"day": day_offset + i + 1})
            for i, r in enumerate(sorted(records, key=lambda x: x.day))
        ]
    return records


def _align_records(
    records: List[DailySymptomRecord], logs: List[str], day_offset: int
) -> List[DailySymptomRecord]:
    by_day = {r.day: r for r in records}
    aligned = []
    for i in range(len(logs)):
        day_num = day_offset + i + 1
        if day_num in by_day:
            aligned.append(by_day[day_num])
        elif records:
            fallback = records[min(i, len(records) - 1)].model_copy(update={"day": day_num})
            aligned.append(fallback)
        else:
            aligned.append(
                DailySymptomRecord(
                    day=day_num,
                    general_wellbeing=1,
                    abdominal_pain=0,
                    liquid_stool_count=0,
                    complications=[],
                    medication_adherence=None,
                )
            )
    return aligned
