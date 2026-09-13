import unittest

from app.schemas import DailySymptomRecord, DayHistory
from app.services.analytics import build_history, compute_stats, _tier


def _day(**kwargs) -> DayHistory:
    defaults = dict(
        day=1,
        date="2026-01-01",
        raw="note",
        hbi=0,
        wellbeing=0,
        wellbeing_label="Very well",
        pain=0,
        pain_label="None",
        liquid=0,
        comps=[],
        meds=True,
    )
    defaults.update(kwargs)
    return DayHistory(**defaults)


class AnalyticsTests(unittest.TestCase):
    def test_hbi_is_sum_of_fields(self):
        rec = DailySymptomRecord(
            day=1,
            general_wellbeing=2,
            abdominal_pain=3,
            liquid_stool_count=4,
            complications=["mouth ulcer", "arthralgia"],
            medication_adherence=True,
        )
        hist = build_history(["raw"], [rec])
        self.assertEqual(hist[0].hbi, 2 + 3 + 4 + 2)

    def test_unmentioned_meds_count_as_taken(self):
        rec = DailySymptomRecord(
            day=1,
            general_wellbeing=0,
            abdominal_pain=0,
            liquid_stool_count=0,
            complications=[],
            medication_adherence=None,
        )
        hist = build_history(["raw"], [rec])
        self.assertTrue(hist[0].meds)

    def test_fourteen_day_windows(self):
        history = [_day(day=i, hbi=0 if i <= 5 else (10 if i >= 10 else 4)) for i in range(1, 15)]
        stats = compute_stats(history)
        self.assertEqual(stats.baseline_window, "Days 1–5")
        self.assertEqual(stats.current_window, "Days 10–14")
        self.assertEqual(stats.baseline_hbi_avg, 0.0)
        self.assertEqual(stats.current_hbi_avg, 10.0)
        self.assertEqual(stats.hbi_trend_delta, 10.0)
        self.assertEqual(stats.clinical_tier, "Moderate/severe flare")

    def test_third_windows_for_other_lengths(self):
        history = [_day(day=i, hbi=1) for i in range(1, 10)]
        stats = compute_stats(history)
        self.assertEqual(stats.baseline_window, "Days 1–3")
        self.assertEqual(stats.current_window, "Days 7–9")

    def test_tiers(self):
        self.assertEqual(_tier(0), "Remission")
        self.assertEqual(_tier(4.9), "Remission")
        self.assertEqual(_tier(5), "Mild activity")
        self.assertEqual(_tier(7.9), "Mild activity")
        self.assertEqual(_tier(8), "Moderate/severe flare")

    def test_adherence_percent(self):
        history = [
            _day(day=1, meds=True),
            _day(day=2, meds=False),
            _day(day=3, meds=True),
            _day(day=4, meds=True),
        ]
        stats = compute_stats(history)
        self.assertEqual(stats.medication_adherence_percent, 75.0)
        self.assertEqual(stats.missed_medication_days, [2])


if __name__ == "__main__":
    unittest.main()
