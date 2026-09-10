from typing import List, Optional

from pydantic import BaseModel, Field


class DailySymptomRecord(BaseModel):
    day: int
    general_wellbeing: int = Field(
        ...,
        ge=0,
        le=4,
        description="0=Very well, 1=Slightly below par, 2=Poor, 3=Very poor, 4=Terrible",
    )
    abdominal_pain: int = Field(..., ge=0, le=3, description="0=None, 1=Mild, 2=Moderate, 3=Severe")
    liquid_stool_count: int = Field(
        ...,
        ge=0,
        description="Count of loose or liquid bowel movements (Bristol 6 or 7 only). Solid stools = 0.",
    )
    complications: List[str] = Field(
        default_factory=list,
        description="Extraintestinal symptoms: arthralgia, mouth ulcers, etc.",
    )
    medication_adherence: Optional[bool] = Field(
        None,
        description="True if meds confirmed taken, False if missed, None if unmentioned.",
    )


class BatchSymptoms(BaseModel):
    records: List[DailySymptomRecord]


class AnalyzeRequest(BaseModel):
    preset_id: Optional[str] = None
    logs: Optional[List[str]] = None
    text: Optional[str] = None


class DayHistory(BaseModel):
    day: int
    date: str
    raw: str
    hbi: int
    wellbeing: int
    wellbeing_label: str
    pain: int
    pain_label: str
    liquid: int
    comps: List[str]
    meds: bool


class StatsSummary(BaseModel):
    monitoring_window_days: int
    baseline_hbi_avg: float
    current_hbi_avg: float
    hbi_trend_delta: float
    medication_adherence_percent: float
    missed_medication_days: List[int]
    adherence_detail: str
    total_liquid_stools_reported: int
    reported_complications: List[str]
    clinical_tier: str
    baseline_window: str
    current_window: str


class AnalyzeResponse(BaseModel):
    report_id: str
    source_label: str
    stats: StatsSummary
    history: List[DayHistory]
    summary: str
    chart_png_b64: str
    rag_context: dict
