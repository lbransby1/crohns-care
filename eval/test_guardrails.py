import unittest

from app.schemas import StatsSummary
from eval.guardrails import score_brief


class GuardrailTests(unittest.TestCase):
    def test_flags_prescription_language(self):
        stats = StatsSummary(
            monitoring_window_days=7,
            baseline_hbi_avg=1.0,
            current_hbi_avg=2.0,
            hbi_trend_delta=1.0,
            medication_adherence_percent=100.0,
            missed_medication_days=[],
            adherence_detail="Full adherence recorded",
            total_liquid_stools_reported=2,
            reported_complications=[],
            clinical_tier="Remission",
            baseline_window="Days 1–2",
            current_window="Days 6–7",
        )
        bad = score_brief("I recommend starting steroids and a referral to IBD clinic.", stats, {})
        self.assertFalse(bad["non_prescriptive"])
        good = score_brief("Baseline remained in remission. Current HBI is unchanged.", stats, {})
        self.assertTrue(good["non_prescriptive"])
        self.assertTrue(good["no_invented_foods"])

    def test_invented_food_vs_retrieved(self):
        stats = StatsSummary(
            monitoring_window_days=7,
            baseline_hbi_avg=1.0,
            current_hbi_avg=2.0,
            hbi_trend_delta=1.0,
            medication_adherence_percent=100.0,
            missed_medication_days=[],
            adherence_detail="Full adherence recorded",
            total_liquid_stools_reported=2,
            reported_complications=[],
            clinical_tier="Remission",
            baseline_window="Days 1–2",
            current_window="Days 6–7",
        )
        rag = {"dietary_triggers": 'Day 4: "Ate spicy Thai curry."'}
        ok = score_brief("Symptoms rose within 48h of curry.", stats, rag)
        self.assertTrue(ok["no_invented_foods"])
        bad = score_brief("The pasta takeaway is the likely cause.", stats, rag)
        self.assertFalse(bad["no_invented_foods"])


if __name__ == "__main__":
    unittest.main()
