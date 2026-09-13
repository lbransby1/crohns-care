"""Regex guardrails on synthesis text. No second model required."""

from __future__ import annotations

import re

from app.schemas import StatsSummary

PRESCRIBE = re.compile(
    r"\b(should (start|stop|take|increase|decrease)|recommend(ed|ing)?|refer(ral)? to|prescribe|switch to)\b",
    re.I,
)
FOOD_WORDS = re.compile(
    r"\b(curry|chicken|pasta|takeaway|oats|salmon|toast|thai|spicy)\b",
    re.I,
)


def score_brief(text: str, stats: StatsSummary, rag_context: dict[str, str]) -> dict:
    blob = text or ""
    allowed = " ".join(rag_context.values()) + " " + stats.adherence_detail
    foods_in_brief = {m.group(0).lower() for m in FOOD_WORDS.finditer(blob)}
    foods_allowed = {m.group(0).lower() for m in FOOD_WORDS.finditer(allowed)}
    invented_foods = sorted(foods_in_brief - foods_allowed)
    missed_ok = all(str(day) in blob for day in stats.missed_medication_days) or not stats.missed_medication_days
    return {
        "non_prescriptive": not bool(PRESCRIBE.search(blob)),
        "word_count": len(blob.split()),
        "under_180": len(blob.split()) <= 200,
        "invented_foods": invented_foods,
        "no_invented_foods": not invented_foods,
        "mentions_missed_days": missed_ok,
    }
