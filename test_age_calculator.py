"""
End-to-end regression tests for the Age Calculator CLI.

The suite intentionally exercises:
- DateParser happy-path formats (ISO/US/EU, natural language, ordinal variations)
- Relative expressions, Julian/ISO week formats, fiscal quarters, and month/year fallbacks
- Numeric parsing pathways (compact integers, Excel serials, Unix timestamps)
- Validation, bounds checking, and error handling safeguards
- AgeCalculator math across calendar boundaries, leap years, and future-date rejection
- Human-readable formatting, including pluralization edge cases
- Integration flows covering CLI argument mode and interactive prompts
"""

import datetime
import io
import os
import sys
import time
import unittest
from contextlib import redirect_stdout
from unittest import mock

from age_calculator import (
    AgeCalculator,
    AgeCalculatorApp,
    AgeResult,
    DateParser,
    main,
)


class DateParserStandardFormatTests(unittest.TestCase):
    def test_iso_formats(self):
        cases = [
            ("1995-12-25", datetime.date(1995, 12, 25)),
            ("1990/12/25", datetime.date(1990, 12, 25)),
            ("2010 03 15", datetime.date(2010, 3, 15)),
            ("2000.01.01", datetime.date(2000, 1, 1)),
        ]
        for raw, expected in cases:
            with self.subTest(raw=raw):
                self.assertEqual(DateParser.parse_date(raw), expected)

    def test_us_formats(self):
        cases = [
            ("12/25/1995", datetime.date(1995, 12, 25)),
            ("01-15-2000", datetime.date(2000, 1, 15)),
            ("03.31.2010", datetime.date(2010, 3, 31)),
            ("06 04 1990", datetime.date(1990, 6, 4)),
        ]
        for raw, expected in cases:
            with self.subTest(raw=raw):
                self.assertEqual(DateParser.parse_date(raw), expected)

    def test_european_formats(self):
        cases = [
            ("25/12/1995", datetime.date(1995, 12, 25)),
            ("31.03.2010", datetime.date(2010, 3, 31)),
            ("15-01-2000", datetime.date(2000, 1, 15)),
            ("25 12 1995", datetime.date(1995, 12, 25)),
        ]
        for raw, expected in cases:
            with self.subTest(raw=raw):
                self.assertEqual(DateParser.parse_date(raw), expected)


class DateParserNaturalLanguageAndOrdinalsTests(unittest.TestCase):
    def test_full_and_abbreviated_months(self):
        cases = [
            ("December 25, 1990", datetime.date(1990, 12, 25)),
            ("25 December 1990", datetime.date(1990, 12, 25)),
            ("Dec 25 1990", datetime.date(1990, 12, 25)),
            ("25-Dec-1990", datetime.date(1990, 12, 25)),
        ]
        for raw, expected in cases:
            with self.subTest(raw=raw):
                self.assertEqual(DateParser.parse_date(raw), expected)

    def test_ordinals_and_day_of_month_phrases(self):
        cases = [
            ("15th January, 2001", datetime.date(2001, 1, 15)),
            ("December 1st, 2000", datetime.date(2000, 12, 1)),
            ("25 of December 2005", datetime.date(2005, 12, 25)),
            ("25th of December 2005", datetime.date(2005, 12, 25)),
        ]
        for raw, expected in cases:
            with self.subTest(raw=raw):
                self.assertEqual(DateParser.parse_date(raw), expected)

    def test_case_insensitivity(self):
        cases = [
            ("jAnUaRy 15, 2001", datetime.date(2001, 1, 15)),
            ("DECEMBER 25, 1990", datetime.date(1990, 12, 25)),
            ("march 1st, 2020", datetime.date(2020, 3, 1)),
        ]
        for raw, expected in cases:
            with self.subTest(raw=raw):
                self.assertEqual(DateParser.parse_date(raw), expected)


class DateParserRelativeAndSpecialTests(unittest.TestCase):
    def test_relative_keywords(self):
        today = datetime.date.today()
        cases = [
            ("today", today),
            ("yesterday", today - datetime.timedelta(days=1)),
            ("tomorrow", today + datetime.timedelta(days=1)),
            ("last year", today - datetime.timedelta(days=365)),
        ]
        for raw, expected in cases:
            with self.subTest(raw=raw):
                self.assertEqual(DateParser.parse_date(raw), expected)

    def test_julian_and_iso_week_dates(self):
        self.assertEqual(DateParser.parse_date("2023-359"), datetime.date(2023, 12, 25))
        self.assertEqual(DateParser.parse_date("2025-W37-2"), datetime.date(2025, 9, 9))

    def test_fiscal_quarters_and_month_year_fallbacks(self):
        self.assertEqual(DateParser.parse_date("2023-Q4"), datetime.date(2023, 10, 1))
        self.assertEqual(DateParser.parse_date("2023 Q1"), datetime.date(2023, 1, 1))
        self.assertEqual(DateParser.parse_date("Dec 1990"), datetime.date(1990, 12, 1))
        self.assertEqual(DateParser.parse_date("1990"), datetime.date(1990, 1, 1))


class DateParserNumericParsingTests(unittest.TestCase):
    def test_eight_digit_numeric_formats(self):
        self.assertEqual(DateParser.parse_date("19991205"), datetime.date(1999, 12, 5))
        self.assertEqual(DateParser.parse_date("12051999"), datetime.date(1999, 5, 12))

    def test_six_digit_numeric_formats(self):
        self.assertEqual(DateParser.parse_date("102598"), datetime.date(1998, 10, 25))
        self.assertEqual(DateParser.parse_date("251098"), datetime.date(1998, 10, 25))

    def test_year_first_six_digit_format(self):
        self.assertEqual(DateParser.parse_date("900101"), datetime.date(1990, 1, 1))

    def test_excel_serial_numbers(self):
        self.assertEqual(DateParser.parse_date("36526"), datetime.date(2000, 1, 1))
        self.assertEqual(DateParser.parse_date("59"), datetime.date(1900, 2, 28))

    def test_invalid_excel_serials_and_numeric_noise(self):
        for raw in ["00000", "99999999", "abcdef"]:
            with self.subTest(raw=raw):
                self.assertIsNone(DateParser.parse_date(raw))

    def test_unix_timestamps_and_timezone_independence(self):
        self.assertEqual(DateParser.parse_date("0"), datetime.date(1970, 1, 1))
        self.assertEqual(DateParser.parse_date("1609459200"), datetime.date(2021, 1, 1))

        if hasattr(time, "tzset"):
            original = os.environ.get("TZ")
            try:
                os.environ["TZ"] = "US/Pacific"
                time.tzset()
                self.assertEqual(DateParser.parse_date("0"), datetime.date(1970, 1, 1))
            finally:
                if original is None:
                    os.environ.pop("TZ", None)
                else:
                    os.environ["TZ"] = original
                time.tzset()


class DateParserValidationTests(unittest.TestCase):
    def test_invalid_inputs_return_none(self):
        bad_inputs = [
            "not a real date",
            "99/99/9999",
            "",
            "   ",
            12345,
            "2023-13-01",
        ]
        for raw in bad_inputs:
            with self.subTest(raw=raw):
                self.assertIsNone(DateParser.parse_date(raw))

    def test_bounds_enforcement(self):
        self.assertIsNone(DateParser.parse_date("1889-12-31"))
        self.assertIsNone(DateParser.parse_date("2101-01-01"))


class AgeCalculatorComputationTests(unittest.TestCase):
    def setUp(self):
        self.today = datetime.date(2025, 9, 9)

    def test_age_when_birthday_passed(self):
        birthday = datetime.date(1990, 8, 20)
        result = AgeCalculator.calculate_age(birthday, today=self.today)
        self.assertEqual((result.years, result.months, result.days), (35, 0, 20))
        self.assertEqual(result.birth_day_of_week, "Monday")

    def test_age_when_birthday_upcoming(self):
        birthday = datetime.date(1990, 10, 30)
        result = AgeCalculator.calculate_age(birthday, today=self.today)
        self.assertEqual((result.years, result.months, result.days), (34, 10, 10))
        self.assertEqual(result.next_birthday_in_days, 51)

    def test_future_dates_raise(self):
        birthday = datetime.date(2026, 1, 1)
        with self.assertRaisesRegex(ValueError, "future"):
            AgeCalculator.calculate_age(birthday, today=self.today)


class AgeCalculatorLeapYearTests(unittest.TestCase):
    def test_feb_29_on_leap_year(self):
        mock_today = datetime.date(2024, 2, 29)
        birthday = datetime.date(2000, 2, 29)
        result = AgeCalculator.calculate_age(birthday, today=mock_today)
        self.assertEqual((result.years, result.months, result.days), (24, 0, 0))

    def test_feb_29_on_non_leap_year(self):
        mock_today = datetime.date(2025, 3, 1)
        birthday = datetime.date(2000, 2, 29)
        result = AgeCalculator.calculate_age(birthday, today=mock_today)
        self.assertEqual((result.years, result.months, result.days), (25, 0, 1))


class AgeCalculatorFormattingTests(unittest.TestCase):
    def test_full_pluralized_output(self):
        age_data = AgeResult(33, 8, 12, 12309, "Monday", 110)
        output = AgeCalculator.format_age_output(datetime.date(1990, 1, 1), age_data)
        self.assertIn("33 years, 8 months and 12 days", output)
        self.assertIn("110 days", output)

    def test_singular_components(self):
        age_data = AgeResult(1, 1, 1, 397, "Tuesday", 1)
        output = AgeCalculator.format_age_output(datetime.date(2024, 8, 6), age_data)
        self.assertIn("1 year, 1 month and 1 day", output)
        self.assertIn("Your next birthday is in 1 day!", output)

    def test_days_only_output(self):
        age_data = AgeResult(0, 0, 1, 1, "Monday", 364)
        output = AgeCalculator.format_age_output(datetime.date(2025, 9, 8), age_data)
        self.assertIn("1 day", output)
        self.assertNotIn("month", output)
        self.assertNotIn("year", output)

    def test_happy_birthday_message(self):
        age_data = AgeResult(20, 0, 0, 7305, "Friday", 0)
        output = AgeCalculator.format_age_output(datetime.date(2005, 9, 9), age_data)
        self.assertIn("Happy Birthday!", output)


class IntegrationAndCliTests(unittest.TestCase):
    def test_complete_workflow(self):
        birthday = DateParser.parse_date("1990-12-25")
        self.assertIsNotNone(birthday)
        assert birthday is not None
        age_result = AgeCalculator.calculate_age(birthday, today=datetime.date(2025, 9, 9))
        output = AgeCalculator.format_age_output(birthday, age_result)
        self.assertIn("Tuesday", output)
        self.assertIn("December 25, 1990", output)

    def test_main_with_argument(self):
        test_args = ["age_calculator.py", "1990-12-25"]
        with mock.patch.object(sys, "argv", test_args):
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                main()
        out = buffer.getvalue()
        self.assertIn("Born on a", out)
        self.assertIn("1990", out)

    def test_main_with_invalid_argument(self):
        test_args = ["age_calculator.py", "not-a-real-date"]
        with mock.patch.object(sys, "argv", test_args):
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                main()
        out = buffer.getvalue()
        self.assertIn("not recognized", out)

    def test_interactive_app_flow(self):
        parser = DateParser()
        calculator = AgeCalculator()
        fake_birthday = datetime.date(2000, 1, 1)
        fake_age = AgeResult(24, 0, 0, 8760, "Saturday", 0)

        with mock.patch.object(DateParser, "parse_date", return_value=fake_birthday), mock.patch.object(
            AgeCalculator, "calculate_age", return_value=fake_age
        ):
            with mock.patch("builtins.input", side_effect=["2000-01-01", "exit"]):
                buffer = io.StringIO()
                with redirect_stdout(buffer):
                    AgeCalculatorApp(parser, calculator).run()

        out = buffer.getvalue()
        self.assertIn("Age Calculator", out)
        self.assertIn("Happy Birthday!", out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
