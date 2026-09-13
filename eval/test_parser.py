import unittest

from app.services.parser import parse_log_document


class ParserTests(unittest.TestCase):
    def test_strips_day_prefix_and_blanks(self):
        raw = """# comment

Day 1: Felt fine. Took azathioprine.


Day 5: Mild cramps, two loose stools.

Day 12: Three liquid stools.
"""
        logs = parse_log_document(raw)
        self.assertEqual(len(logs), 3)
        self.assertTrue(logs[0].startswith("Felt fine"))
        self.assertIn("Mild cramps", logs[1])
        self.assertIn("liquid", logs[2])

    def test_json_logs_array(self):
        logs = parse_log_document('{"logs": ["a", "b"]}')
        self.assertEqual(logs, ["a", "b"])

    def test_rejects_empty(self):
        with self.assertRaises(ValueError):
            parse_log_document("   \n# only comments\n")


if __name__ == "__main__":
    unittest.main()
