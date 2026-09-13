import unittest

from eval.gold import pack_batches, render_note, sample_dataset, sample_day
from eval.metrics import gold_hbi, score_pairs
from app.schemas import DailySymptomRecord
import random


class GoldRendererTests(unittest.TestCase):
    def test_dataset_size_and_styles(self):
        days = sample_dataset(n=80, seed=1)
        self.assertEqual(len(days), 80)
        styles = {d.style for d in days}
        self.assertTrue({"clinic", "informal", "terse", "bristol_ambiguous"} <= styles)

    def test_formed_notes_are_not_bristol_6(self):
        rng = random.Random(0)
        for _ in range(40):
            gold = sample_day(rng, "clinic")
            if gold.formed_stool:
                self.assertEqual(gold.record.liquid_stool_count, 0)
                self.assertNotIn("Bristol 6", gold.note)
                self.assertNotIn("diarrhea", gold.note.lower())

    def test_missed_meds_are_lexical(self):
        rec = DailySymptomRecord(
            day=1,
            general_wellbeing=1,
            abdominal_pain=1,
            liquid_stool_count=2,
            complications=[],
            medication_adherence=False,
        )
        note = render_note(rec, "clinic", formed_stool=False)
        self.assertIn("Skipped", note)

    def test_unmentioned_meds_omit_aza(self):
        rec = DailySymptomRecord(
            day=1,
            general_wellbeing=0,
            abdominal_pain=0,
            liquid_stool_count=0,
            complications=[],
            medication_adherence=None,
        )
        note = render_note(rec, "clinic", formed_stool=True)
        self.assertNotIn("azathioprine", note.lower())
        self.assertNotIn("skipped", note.lower())

    def test_perfect_extraction_scores_one(self):
        days = sample_dataset(n=20, seed=2)
        batches = pack_batches(days, batch_size=10)
        pairs = [(g, g.record) for batch in batches for g in batch]
        summary = score_pairs(pairs)
        self.assertEqual(summary["overall"]["wb_acc"], 1.0)
        self.assertEqual(summary["overall"]["hbi_acc"], 1.0)
        self.assertEqual(summary["overall"]["adh_acc"], 1.0)

    def test_informal_notes_are_a_distribution(self):
        rec = DailySymptomRecord(
            day=1,
            general_wellbeing=1,
            abdominal_pain=1,
            liquid_stool_count=2,
            complications=["mouth ulcer"],
            medication_adherence=False,
        )
        notes = {render_note(rec, "informal", False, random.Random(i)) for i in range(40)}
        self.assertGreaterEqual(len(notes), 12)
        joined = " ".join(notes).lower()
        self.assertNotIn("bit meh today", joined)

    def test_hbi_formula(self):
        rec = DailySymptomRecord(
            day=1,
            general_wellbeing=1,
            abdominal_pain=2,
            liquid_stool_count=3,
            complications=["mouth ulcer"],
            medication_adherence=True,
        )
        self.assertEqual(gold_hbi(rec), 7)


if __name__ == "__main__":
    unittest.main()
