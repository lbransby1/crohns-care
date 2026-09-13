"""Planted-span recall for temporal Chroma retrieval (no LLM)."""

from __future__ import annotations

import re

from app.schemas import DailySymptomRecord
from app.services.analytics import build_history
from app.services.rag import retrieve_context

DAY_RE = re.compile(r"\[Day (\d+)")


def planted_diary() -> tuple[list[str], list[DailySymptomRecord], dict[str, int]]:
    """Clinic-style 12-day diary with one distinctive span per RAG bucket."""
    logs = [
        "Felt very well. No pain. One formed Bristol 4 stool. Took azathioprine.",
        "Felt very well. No pain. One formed stool. Chicken and rice. Meds taken.",
        "Felt well. Gym. Solid bowel movement. Azathioprine confirmed.",
        "Felt well. Ate spicy Thai curry for dinner. One formed Bristol 4 stool. Took azathioprine.",
        "Felt slightly below par. Mild bloating. Formed stool. Meds taken.",
        "Mild cramps. Two mushy stools. Skipped the evening azathioprine dose by mistake.",
        "Felt below par. One formed stool. Took azathioprine.",
        "Energy low. Formed stool. Meds taken.",
        "A mouth ulcer appeared. Three watery stools. Moderate pain. Took azathioprine.",
        "Ulcer smaller. Two loose stools. Meds taken.",
        "Severe cramping. Five watery diarrhea episodes. Poor energy. Took azathioprine.",
        "Felt very well. One formed stool. Azathioprine confirmed. Sleeping through.",
    ]
    records = [
        DailySymptomRecord(day=1, general_wellbeing=0, abdominal_pain=0, liquid_stool_count=0, complications=[], medication_adherence=True),
        DailySymptomRecord(day=2, general_wellbeing=0, abdominal_pain=0, liquid_stool_count=0, complications=[], medication_adherence=True),
        DailySymptomRecord(day=3, general_wellbeing=0, abdominal_pain=0, liquid_stool_count=0, complications=[], medication_adherence=True),
        DailySymptomRecord(day=4, general_wellbeing=0, abdominal_pain=0, liquid_stool_count=0, complications=[], medication_adherence=True),
        DailySymptomRecord(day=5, general_wellbeing=1, abdominal_pain=0, liquid_stool_count=0, complications=[], medication_adherence=True),
        DailySymptomRecord(day=6, general_wellbeing=1, abdominal_pain=1, liquid_stool_count=0, complications=[], medication_adherence=False),
        DailySymptomRecord(day=7, general_wellbeing=1, abdominal_pain=0, liquid_stool_count=0, complications=[], medication_adherence=True),
        DailySymptomRecord(day=8, general_wellbeing=1, abdominal_pain=0, liquid_stool_count=0, complications=[], medication_adherence=True),
        DailySymptomRecord(day=9, general_wellbeing=2, abdominal_pain=2, liquid_stool_count=3, complications=["mouth ulcer"], medication_adherence=True),
        DailySymptomRecord(day=10, general_wellbeing=1, abdominal_pain=1, liquid_stool_count=2, complications=["mouth ulcer"], medication_adherence=True),
        DailySymptomRecord(day=11, general_wellbeing=3, abdominal_pain=3, liquid_stool_count=5, complications=[], medication_adherence=True),
        DailySymptomRecord(day=12, general_wellbeing=0, abdominal_pain=0, liquid_stool_count=0, complications=[], medication_adherence=True),
    ]
    plants = {
        "dietary_triggers": 4,
        "medication": 6,
        "complications": 9,
        "stool_pattern": 11,
    }
    return logs, records, plants


def days_in_hits(formatted: str) -> set[int]:
    return {int(m) for m in DAY_RE.findall(formatted or "")}


def score_rag() -> dict:
    logs, records, plants = planted_diary()
    history = build_history(logs, records)
    context = retrieve_context(history)
    hits = {bucket: days_in_hits(text) for bucket, text in context.items()}
    found = {bucket: plants[bucket] in hits.get(bucket, set()) for bucket in plants}
    recall = sum(found.values()) / len(plants)
    return {
        "recall_at_3": recall,
        "found": found,
        "hits": {k: sorted(v) for k, v in hits.items()},
        "plants": plants,
    }
