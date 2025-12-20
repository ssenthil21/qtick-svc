import unittest
from app.utils.date_utils import parse_date_flexible
from datetime import datetime, timedelta

class TestDateParsing(unittest.TestCase):
    def test_today(self):
        result = parse_date_flexible("today")
        expected_prefix = datetime.now().strftime("%Y-%m-%d")
        self.assertTrue(result.startswith(expected_prefix))
        print(f"today: {result}")

    def test_tomorrow(self):
        result = parse_date_flexible("tomorrow")
        expected_prefix = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        self.assertTrue(result.startswith(expected_prefix))
        print(f"tomorrow: {result}")

    def test_next_monday(self):
        result = parse_date_flexible("next monday")
        print(f"next monday: {result}")
        # Not asserting exact date as it depends on current weekday, but verifying format
        self.assertRegex(result, r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.000\+0000")

    def test_specific_date(self):
        result = parse_date_flexible("dec 24 2025")
        self.assertTrue(result.startswith("2025-12-24"))
        print(f"dec 24 2025: {result}")

    def test_iso_passthrough(self):
        # Even if it's already ISO, dateparser should handle it and reformulate to our exact needs
        iso_str = "2025-12-20T15:33:46.000+0000"
        result = parse_date_flexible(iso_str)
        self.assertEqual(result, iso_str)
        print(f"ISO: {result}")

if __name__ == "__main__":
    unittest.main()
