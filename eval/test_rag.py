import unittest

from eval.rag_eval import planted_diary, score_rag


class RagEvalTests(unittest.TestCase):
    def test_planted_diary_length(self):
        logs, records, plants = planted_diary()
        self.assertEqual(len(logs), 12)
        self.assertEqual(len(records), 12)
        self.assertEqual(set(plants), {"dietary_triggers", "medication", "complications", "stool_pattern"})

    def test_retrieve_context_returns_buckets(self):
        result = score_rag()
        self.assertEqual(set(result["hits"]), {"dietary_triggers", "medication", "complications", "stool_pattern"})
        self.assertGreaterEqual(result["recall_at_3"], 0.0)
        self.assertLessEqual(result["recall_at_3"], 1.0)


if __name__ == "__main__":
    unittest.main()
