from datetime import datetime, timedelta

from app.config import PAIN_LABELS, WELLBEING_LABELS
from app.schemas import DailySymptomRecord, DayHistory, StatsSummary


def build_history(logs: list[str], records: list[DailySymptomRecord]) -> list[DayHistory]:
    base_date = datetime.now() - timedelta(days=len(logs))
    history: list[DayHistory] = []
    for i, (note, ext) in enumerate(zip(logs, records), start=1):
        hbi = (
            ext.general_wellbeing
            + ext.abdominal_pain
            + ext.liquid_stool_count
            + len(ext.complications)
        )
        history.append(
            DayHistory(
                day=i,
                date=(base_date + timedelta(days=i - 1)).strftime("%Y-%m-%d"),
                raw=note,
                hbi=hbi,
                wellbeing=ext.general_wellbeing,
                wellbeing_label=WELLBEING_LABELS.get(ext.general_wellbeing, "Unknown"),
                pain=ext.abdominal_pain,
                pain_label=PAIN_LABELS.get(ext.abdominal_pain, "Unknown"),
                liquid=ext.liquid_stool_count,
                comps=ext.complications,
                meds=ext.medication_adherence if ext.medication_adherence is not None else True,
            )
        )
    return history


def compute_stats(history: list[DayHistory]) -> StatsSummary:
    total_days = len(history)
    baseline, current, baseline_label, current_label = _windows(history)

    baseline_hbi = sum(d.hbi for d in baseline) / len(baseline)
    current_hbi = sum(d.hbi for d in current) / len(current)
    missed_days = [d.day for d in history if not d.meds]

    cleaned_comps: set[str] = set()
    for day in history:
        for comp in day.comps:
            normalized = comp.lower().replace(" ulcers", " ulcer")
            normalized = normalized.replace("left knee swollen", "knee swelling")
            cleaned_comps.add(normalized.capitalize())

    if not missed_days:
        adherence_detail = "Full adherence recorded"
    elif len(missed_days) == 1:
        adherence_detail = f"Missed dose on Day {missed_days[0]}"
    else:
        joined = ", ".join(str(d) for d in missed_days)
        adherence_detail = f"Missed dose on Days {joined}"

    delta = current_hbi - baseline_hbi
    return StatsSummary(
        monitoring_window_days=total_days,
        baseline_hbi_avg=round(baseline_hbi, 1),
        current_hbi_avg=round(current_hbi, 1),
        hbi_trend_delta=round(delta, 1),
        medication_adherence_percent=round(
            (sum(1 for d in history if d.meds) / total_days) * 100, 1
        ),
        missed_medication_days=missed_days,
        adherence_detail=adherence_detail,
        total_liquid_stools_reported=sum(d.liquid for d in history),
        reported_complications=sorted(cleaned_comps),
        clinical_tier=_tier(current_hbi),
        baseline_window=baseline_label,
        current_window=current_label,
    )


def _windows(history: list[DayHistory]):
    n = len(history)
    if n == 1:
        return history, history, "Day 1", "Day 1"
    if n == 14:
        baseline = [d for d in history if 1 <= d.day <= 5]
        current = [d for d in history if 10 <= d.day <= 14]
        return baseline, current, "Days 1–5", "Days 10–14"

    k = max(1, n // 3)
    baseline = history[:k]
    current = history[-k:]
    return (
        baseline,
        current,
        f"Days {baseline[0].day}–{baseline[-1].day}",
        f"Days {current[0].day}–{current[-1].day}",
    )


def _tier(current_hbi: float) -> str:
    if current_hbi < 5:
        return "Remission"
    if current_hbi < 8:
        return "Mild activity"
    return "Moderate/severe flare"
