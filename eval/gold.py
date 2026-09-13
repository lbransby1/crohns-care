"""Sample gold HBI labels first, then render a note that encodes them."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import List, Optional

from app.schemas import DailySymptomRecord

STYLES = ("clinic", "informal", "terse", "bristol_ambiguous")
COMPLICATION_VOCAB = ("mouth ulcer", "arthralgia", "knee swelling")

WELLBEING_CLINIC = {
    0: "Felt very well.",
    1: "Felt slightly below par.",
    2: "Felt poor.",
    3: "Felt very poor.",
    4: "Felt terrible.",
}
PAIN_CLINIC = {
    0: "No abdominal pain.",
    1: "Mild abdominal cramps.",
    2: "Moderate abdominal pain.",
    3: "Severe abdominal cramping.",
}

# Independent paraphrase banks. Sample one string per field so informal is a
# distribution, not a single catchphrase per HBI value.
WELLBEING_INFORMAL = {
    0: ("all good today", "pretty normal", "feeling myself", "decent day", "not bad at all"),
    1: ("a bit off", "not 100%", "slightly crap", "under the weather", "blah energy"),
    2: ("washed out", "dragging all day", "poorly", "really run down", "gut-day kind of tired"),
    3: ("grim", "horrible day", "exhausted and low", "barely holding it together", "very poor form"),
    4: ("couldn't function", "in bits", "worst it's been", "utterly wiped", "couldn't get off the sofa"),
}
PAIN_INFORMAL = {
    0: ("tummy quiet", "no belly pain", "gut behaving", "abdomen fine"),
    1: ("twinges", "slight ache lower down", "mild cramp after lunch", "a bit gripey"),
    2: ("proper cramps", "sore on the right", "moderate belly pain", "cramping in waves"),
    3: ("doubling over", "pain before every loo trip", "severe belly cramps", "had to stop walking"),
}
STOOL_FORMED_INFORMAL = (
    "one solid poo",
    "normal bm",
    "bristol 4 once",
    "formed stool this morning",
    "usual solid bowel movement",
)
STOOL_LIQUID_INFORMAL = (
    "{n} watery trips to the loo",
    "{n} liquid stools",
    "on the toilet {n} times, all watery",
    "{n} bouts of diarrhoea",
    "{n} bristol 6-7 motions",
)
MOUTH_ULCER_INFORMAL = (
    "sore ulcer inside the mouth",
    "ulcer on my lip",
    "painful ulcer on the gum",
    "mouth ulcers again",
    "aphthous ulcer on the cheek",
)
ARTHRALGIA_INFORMAL = (
    "joints aching",
    "achy joints overnight",
    "arthralgia in the hands",
    "stiff painful joints, no swelling",
    "hips painful without any swelling",
)
KNEE_SWELLING_INFORMAL = (
    "puffy swollen knee",
    "knee blown up and swollen",
    "swelling in the left knee",
    "can't get jeans over the swollen knee",
    "knee hot and swollen",
)
MEDS_TAKEN_INFORMAL = (
    "took aza",
    "meds done",
    "remembered both doses",
    "azathioprine taken with breakfast",
    "took the tablets",
)
MEDS_MISSED_INFORMAL = (
    "forgot aza",
    "missed tonight's tablet",
    "skipped the pill",
    "didn't take the evening dose",
    "blanked on the immunosuppressant",
)
FOOD_ASIDE_INFORMAL = (
    "",
    "",
    "",
    "had a creamy pasta",
    "takeaway chicken",
    "leftover curry",
    "just toast",
    "soup and rice",
)

WELLBEING_TERSE = {
    0: ("ok", "fine", "well"),
    1: ("below par", "off", "low energy"),
    2: ("poor", "run down", "washed out"),
    3: ("very poor", "grim", "exhausted"),
    4: ("terrible", "wiped out", "can't function"),
}
PAIN_TERSE = {
    1: ("mild cramps", "slight ache", "twinges"),
    2: ("mod cramps", "right-sided pain", "cramping"),
    3: ("severe cramps", "doubled over", "pain ++"),
}


@dataclass
class GoldDay:
    style: str
    note: str
    record: DailySymptomRecord
    formed_stool: bool
    planted: dict = field(default_factory=dict)

    def gold_hbi(self) -> int:
        rec = self.record
        return rec.general_wellbeing + rec.abdominal_pain + rec.liquid_stool_count + len(rec.complications)


def sample_dataset(n: int = 280, seed: int = 42) -> List[GoldDay]:
    rng = random.Random(seed)
    quotas = {
        "clinic": int(n * 0.35),
        "informal": int(n * 0.25),
        "terse": int(n * 0.20),
        "bristol_ambiguous": n,
    }
    quotas["bristol_ambiguous"] = n - quotas["clinic"] - quotas["informal"] - quotas["terse"]
    days: List[GoldDay] = []
    for style, count in quotas.items():
        for _ in range(max(0, count)):
            days.append(sample_day(rng, style))
    rng.shuffle(days)
    return days


def pack_batches(days: List[GoldDay], batch_size: int = 14) -> List[List[GoldDay]]:
    grouped: dict[str, List[GoldDay]] = {style: [] for style in STYLES}
    for day in days:
        grouped[day.style].append(day)
    batches: List[List[GoldDay]] = []
    for style in STYLES:
        items = grouped[style]
        for start in range(0, len(items), batch_size):
            chunk = items[start : start + batch_size]
            renumbered = []
            for i, gold in enumerate(chunk, start=1):
                rec = gold.record.model_copy(update={"day": i})
                renumbered.append(
                    GoldDay(
                        style=gold.style,
                        note=gold.note,
                        record=rec,
                        formed_stool=gold.formed_stool,
                        planted=gold.planted,
                    )
                )
            batches.append(renumbered)
    return batches


def sample_day(rng: random.Random, style: str) -> GoldDay:
    wellbeing = int(rng.choice([0, 0, 1, 1, 2, 3, 4]))
    pain = int(rng.choice([0, 0, 1, 1, 2, 3]))
    complications = _sample_complications(rng)
    adherence = rng.choice([True, True, False, None])

    formed_stool = True
    if style == "bristol_ambiguous":
        if rng.random() < 0.5:
            liquid = 0
            formed_stool = True
        else:
            liquid = int(rng.choice([1, 2, 3, 4]))
            formed_stool = False
    elif rng.random() < 0.45:
        liquid = 0
        formed_stool = True
    else:
        liquid = int(rng.choice([1, 2, 3, 4, 5]))
        formed_stool = False

    record = DailySymptomRecord(
        day=1,
        general_wellbeing=wellbeing,
        abdominal_pain=pain,
        liquid_stool_count=liquid,
        complications=complications,
        medication_adherence=adherence,
    )
    note = render_note(record, style, formed_stool, rng)
    planted = {}
    if adherence is False:
        planted["missed_meds"] = True
    if complications:
        planted["complications"] = list(complications)
    if liquid:
        planted["liquid"] = liquid
    return GoldDay(style=style, note=note, record=record, formed_stool=formed_stool, planted=planted)


def render_note(
    record: DailySymptomRecord,
    style: str,
    formed_stool: bool,
    rng: Optional[random.Random] = None,
) -> str:
    rng = rng or random.Random(0)
    if style == "informal":
        return _render_informal(record, formed_stool, rng)
    if style == "terse":
        return _render_terse(record, formed_stool, rng)
    if style == "bristol_ambiguous":
        return _render_bristol(record, formed_stool)
    return _render_clinic(record, formed_stool)


def _pick(rng: random.Random, options: tuple[str, ...]) -> str:
    return rng.choice(options)


def _sample_complications(rng: random.Random) -> List[str]:
    roll = rng.random()
    if roll < 0.7:
        return []
    picked = rng.sample(list(COMPLICATION_VOCAB), k=1 if roll < 0.92 else 2)
    return picked


def _stool_clinic(liquid: int, formed: bool) -> str:
    if formed or liquid == 0:
        return "One formed Bristol 4 stool."
    return f"{liquid} watery stools (Bristol 6 or 7)."


def _meds_clinic(adherence: Optional[bool]) -> str:
    if adherence is True:
        return "Took azathioprine as prescribed."
    if adherence is False:
        return "Skipped the evening azathioprine dose."
    return ""


def _comps_clinic(comps: List[str]) -> str:
    bits = []
    if "mouth ulcer" in comps:
        bits.append("A mouth ulcer appeared.")
    if "arthralgia" in comps:
        bits.append("Joint pain / arthralgia in the knees.")
    if "knee swelling" in comps:
        bits.append("Left knee swollen.")
    return " ".join(bits)


def _render_clinic(record: DailySymptomRecord, formed: bool) -> str:
    parts = [
        WELLBEING_CLINIC[record.general_wellbeing],
        PAIN_CLINIC[record.abdominal_pain],
        _stool_clinic(record.liquid_stool_count, formed),
        _comps_clinic(record.complications),
        _meds_clinic(record.medication_adherence),
    ]
    return " ".join(p for p in parts if p)


def _render_informal(record: DailySymptomRecord, formed: bool, rng: random.Random) -> str:
    if formed or record.liquid_stool_count == 0:
        stool = _pick(rng, STOOL_FORMED_INFORMAL)
    else:
        stool = _pick(rng, STOOL_LIQUID_INFORMAL).format(n=record.liquid_stool_count)
    comps = []
    if "mouth ulcer" in record.complications:
        comps.append(_pick(rng, MOUTH_ULCER_INFORMAL))
    if "arthralgia" in record.complications:
        comps.append(_pick(rng, ARTHRALGIA_INFORMAL))
    if "knee swelling" in record.complications:
        comps.append(_pick(rng, KNEE_SWELLING_INFORMAL))
    if record.medication_adherence is True:
        meds = _pick(rng, MEDS_TAKEN_INFORMAL)
    elif record.medication_adherence is False:
        meds = _pick(rng, MEDS_MISSED_INFORMAL)
    else:
        meds = ""
    extra = _pick(rng, FOOD_ASIDE_INFORMAL)
    parts = [
        _pick(rng, WELLBEING_INFORMAL[record.general_wellbeing]),
        _pick(rng, PAIN_INFORMAL[record.abdominal_pain]),
        stool,
        " ".join(comps),
        meds,
        extra,
    ]
    return " ".join(p for p in parts if p)


def _render_terse(record: DailySymptomRecord, formed: bool, rng: random.Random) -> str:
    bits = []
    bits.append(_pick(rng, WELLBEING_TERSE[record.general_wellbeing]))
    if record.abdominal_pain:
        bits.append(_pick(rng, PAIN_TERSE[record.abdominal_pain]))
    if formed or record.liquid_stool_count == 0:
        bits.append(_pick(rng, ("1 stool", "formed bm", "bristol 4")))
    else:
        bits.append(_pick(rng, ("watery x{n}", "{n} liquid", "{n} diarrhea")).format(n=record.liquid_stool_count))
    if "mouth ulcer" in record.complications:
        bits.append(_pick(rng, ("ulcer", "mouth sore", "aphthous ulcer")))
    if "arthralgia" in record.complications:
        bits.append(_pick(rng, ("arthralgia", "joint ache", "stiff knees")))
    if "knee swelling" in record.complications:
        bits.append(_pick(rng, ("knee swollen", "puffy knee", "knee swelling")))
    if record.medication_adherence is True:
        bits.append(_pick(rng, ("aza", "meds taken", "dose done")))
    elif record.medication_adherence is False:
        bits.append(_pick(rng, ("skipped meds", "missed aza", "forgot tablet")))
    return ". ".join(bits)


def _render_bristol(record: DailySymptomRecord, formed: bool) -> str:
    if formed or record.liquid_stool_count == 0:
        stool = "Stool mushy twice, Bristol 5, not watery or liquid."
        liquid_note = "Solid-ish stools only."
    else:
        stool = f"{record.liquid_stool_count} watery stools, Bristol 6-7 only."
        liquid_note = "Count liquid motions, not formed ones."
    parts = [
        WELLBEING_CLINIC[record.general_wellbeing],
        PAIN_CLINIC[record.abdominal_pain],
        stool,
        liquid_note,
        _comps_clinic(record.complications),
        _meds_clinic(record.medication_adherence),
    ]
    return " ".join(p for p in parts if p)
