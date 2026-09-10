import json

from openai import APIError, RateLimitError

from app.config import CEREBRAS_MODEL
from app.schemas import StatsSummary
from app.services.extraction import EXTRA_BODY, get_plain_client


SYNTHESIS_PROMPT = """You are an expert Clinical Data Synthesizer assisting an outpatient gastroenterologist.
Compile a Clinical Outpatient Brief from the patient's daily Crohn's logs.
A visual HBI trajectory chart will be appended. Do not output day-by-day tables.

STRICT CONSTRAINTS:
1. Use ONLY the deterministic metrics and retrieved log chunks provided. Do not invent dates, foods, or doses.
2. Medication: the global adherence percentage belongs only in the top-level picture. Inside phase sections, mention missed doses only on the days they occurred.
3. Write a 3-phase symptom-development narrative using the windows supplied in the metrics (baseline, middle/onset if present, current). Describe how stools, pain, energy, and extra-intestinal signs changed over time.
4. Dietary triggers: only flag a food if it appears in the retrieved chunks AND symptoms worsen within a 24–48h window after it. If the link is weak, say so.
5. NON-PRESCRIPTIVE: never recommend drugs, diets, or referrals. Summarise objective data.
6. Word limit: under 180 words. Use short labelled sections, not markdown headings with hashes.
"""


def synthesize_brief(stats: StatsSummary, rag_context: dict[str, str]) -> str:
    user_prompt = f"""DETERMINISTIC CLINICAL METRICS:
{json.dumps(stats.model_dump(), indent=2)}

QUALITATIVE LOG CHUNKS (temporal RAG):
Potential Dietary Triggers:
{rag_context.get("dietary_triggers", "")}

Complications & Symptoms:
{rag_context.get("complications", "")}

Medication mentions:
{rag_context.get("medication", "")}

Stool pattern:
{rag_context.get("stool_pattern", "")}
"""
    client = get_plain_client()
    delay = 2.0
    last_error = None
    for attempt in range(1, 5):
        try:
            response = client.chat.completions.create(
                model=CEREBRAS_MODEL,
                messages=[
                    {"role": "system", "content": SYNTHESIS_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.1,
                max_tokens=700,
                extra_body=EXTRA_BODY,
            )
            text = (response.choices[0].message.content or "").strip()
            if text:
                return text
            raise RuntimeError("Empty synthesis from the model.")
        except (RateLimitError, APIError, Exception) as exc:
            last_error = exc
            if attempt == 4:
                break
            import time

            time.sleep(delay)
            delay *= 2.0
    raise RuntimeError(f"Summary generation failed: {last_error}")
