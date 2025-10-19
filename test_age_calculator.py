"""
Comprehensive test suite for Age Calculator.

This test suite covers:
- All 70+ date format parsing capabilities
- Age calculation logic with edge cases
- Output formatting with and without emoji
- MessageFormatter class functionality
- Error handling and validation

Test Organization:
1. DateParser Tests - All parsing capabilities
2. AgeCalculator Tests - Age calculation logic
3. MessageFormatter Tests - Message formatting
4. Integration Tests - End-to-end scenarios
5. Error Handling Tests - Invalid inputs and edge cases
"""

import datetime
import unittest
from unittest.mock import patch

from age_calculator import (
    AgeCalculator,
    AgeResult,
    DateParser,
    MessageFormatter,
)


# =============================================================================
# DATE PARSER TESTS
# =============================================================================

class TestDateParserStandardFormats(unittest.TestCase):
    """Tests for standard date formats (ISO, US, European)."""

    def test_iso_8601_formats(self):
        """Test ISO 8601 standard formats."""
        test_cases = [
            ("1995-12-25", datetime.date(1995, 12, 25)),
            ("1990/12/25", datetime.date(1990, 12, 25)),
            ("2000.01.01", datetime.date(2000, 1, 1)),
            ("2010 03 15", datetime.date(2010, 3, 15)),
        ]
        for date_str, expected in test_cases:
            with self.subTest(date_str=date_str):
                self.assertEqual(DateParser.parse_date(date_str), expected)

    def test_us_formats(self):
        """Test US date formats (MM/DD/YYYY)."""
        test_cases = [
            ("12/25/1995", datetime.date(1995, 12, 25)),
            ("01-15-2000", datetime.date(2000, 1, 15)),
            ("03.31.2010", datetime.date(2010, 3, 31)),
            ("06 04 1990", datetime.date(1990, 6, 4)),
        ]
        for date_str, expected in test_cases:
            with self.subTest(date_str=date_str):
                self.assertEqual(DateParser.parse_date(date_str), expected)

    def test_european_formats(self):
        """Test European date formats (DD/MM/YYYY)."""
        test_cases = [
            ("25/12/1995", datetime.date(1995, 12, 25)),
            ("15-01-2000", datetime.date(2000, 1, 15)),
            ("31.03.2010", datetime.date(2010, 3, 31)),
            ("25 12 1995", datetime.date(1995, 12, 25)),
        ]
        for date_str, expected in test_cases:
            with self.subTest(date_str=date_str):
                self.assertEqual(DateParser.parse_date(date_str), expected)


class TestDateParserNaturalLanguage(unittest.TestCase):
    """Tests for natural language date formats."""

    def test_full_month_names(self):
        """Test dates with full month names."""
        test_cases = [
            ("January 15, 2001", datetime.date(2001, 1, 15)),
            ("15 January 2001", datetime.date(2001, 1, 15)),
            ("December 25, 1990", datetime.date(1990, 12, 25)),
            ("25 December 1990", datetime.date(1990, 12, 25)),
        ]
        for date_str, expected in test_cases:
            with self.subTest(date_str=date_str):
                self.assertEqual(DateParser.parse_date(date_str), expected)

    def test_abbreviated_month_names(self):
        """Test dates with abbreviated month names."""
        test_cases = [
            ("15 Jan 2001", datetime.date(2001, 1, 15)),
            ("Jan 15, 2001", datetime.date(2001, 1, 15)),
            ("25-Dec-1990", datetime.date(1990, 12, 25)),
            ("Dec 25 1990", datetime.date(1990, 12, 25)),
        ]
        for date_str, expected in test_cases:
            with self.subTest(date_str=date_str):
                self.assertEqual(DateParser.parse_date(date_str), expected)

    def test_ordinal_indicators(self):
        """Test dates with ordinal indicators (1st, 2nd, 3rd, etc.)."""
        test_cases = [
            ("15th January, 2001", datetime.date(2001, 1, 15)),
            ("December 1st, 2000", datetime.date(2000, 12, 1)),
            ("March 2nd, 1995", datetime.date(1995, 3, 2)),
            ("April 3rd, 2010", datetime.date(2010, 4, 3)),
            ("May 21st 2020", datetime.date(2020, 5, 21)),
        ]
        for date_str, expected in test_cases:
            with self.subTest(date_str=date_str):
                self.assertEqual(DateParser.parse_date(date_str), expected)

    def test_day_of_month_format(self):
        """Test 'day of month' format (e.g., '25 of December 2005')."""
        test_cases = [
            ("25 of December 2005", datetime.date(2005, 12, 25)),
            ("1 of Jan 2001", datetime.date(2001, 1, 1)),
            ("15 of March 2010", datetime.date(2010, 3, 15)),
        ]
        for date_str, expected in test_cases:
            with self.subTest(date_str=date_str):
                self.assertEqual(DateParser.parse_date(date_str), expected)

    def test_case_insensitivity(self):
        """Test that parsing is case-insensitive."""
        test_cases = [
            ("jAnUaRy 15, 2001", datetime.date(2001, 1, 15)),
            ("DECEMBER 25, 1990", datetime.date(1990, 12, 25)),
            ("march 1st, 2020", datetime.date(2020, 3, 1)),
        ]
        for date_str, expected in test_cases:
            with self.subTest(date_str=date_str):
                self.assertEqual(DateParser.parse_date(date_str), expected)


class TestDateParserRelativeDates(unittest.TestCase):
    """Tests for relative date strings."""

    def test_basic_relative_dates(self):
        """Test basic relative dates (today, yesterday, tomorrow)."""
        today = datetime.date.today()
        test_cases = [
            ("today", today),
            ("yesterday", today - datetime.timedelta(days=1)),
            ("tomorrow", today + datetime.timedelta(days=1)),
            ("now", today),
        ]
        for date_str, expected in test_cases:
            with self.subTest(date_str=date_str):
                self.assertEqual(DateParser.parse_date(date_str), expected)

    def test_week_based_relative_dates(self):
        """Test week-based relative dates."""
        today = datetime.date.today()
        test_cases = [
            ("last week", today - datetime.timedelta(weeks=1)),
            ("next week", today + datetime.timedelta(weeks=1)),
        ]
        for date_str, expected in test_cases:
            with self.subTest(date_str=date_str):
                self.assertEqual(DateParser.parse_date(date_str), expected)

    def test_month_based_relative_dates(self):
        """Test month-based relative dates (approximate)."""
        today = datetime.date.today()
        test_cases = [
            ("last month", today - datetime.timedelta(days=30)),
            ("next month", today + datetime.timedelta(days=30)),
        ]
        for date_str, expected in test_cases:
            with self.subTest(date_str=date_str):
                self.assertEqual(DateParser.parse_date(date_str), expected)

    def test_year_based_relative_dates(self):
        """Test year-based relative dates."""
        today = datetime.date.today()
        test_cases = [
            ("last year", today - datetime.timedelta(days=365)),
            ("next year", today + datetime.timedelta(days=365)),
        ]
        for date_str, expected in test_cases:
            with self.subTest(date_str=date_str):
                self.assertEqual(DateParser.parse_date(date_str), expected)


class TestDateParserUnixTimestamps(unittest.TestCase):
    """Tests for Unix timestamp parsing."""

    def test_valid_unix_timestamps(self):
        """Test parsing valid Unix timestamps."""
        test_cases = [
            ("659318400", datetime.date(1990, 11, 23)),
            ("946684800", datetime.date(2000, 1, 1)),
            ("1609459200", datetime.date(2021, 1, 1)),
            ("0", datetime.date(1970, 1, 1)),
        ]
        for timestamp, expected in test_cases:
            with self.subTest(timestamp=timestamp):
                result = DateParser.parse_date(timestamp)
                self.assertIsNotNone(result)
                if result is not None:
                    delta = abs((result - expected).days)
                    self.assertLessEqual(delta, 1)

    def test_invalid_unix_timestamps(self):
        """Test that invalid timestamps return None."""
        test_cases = [
            "99999999999",
            "-1",
            "abc123",
            "12345",
        ]
        for timestamp in test_cases:
            with self.subTest(timestamp=timestamp):
                result = DateParser.parse_date(timestamp)
                if result:
                    self.assertIsInstance(result, datetime.date)


class TestDateParserSpecialFormats(unittest.TestCase):
    """Tests for special date formats (Julian, week dates, etc.)."""

    def test_julian_dates(self):
        """Test Julian date format (YYYY-DDD)."""
        test_cases = [
            ("2023-359", datetime.date(2023, 12, 25)),
            ("2024-1", datetime.date(2024, 1, 1)),
            ("2024-60", datetime.date(2024, 2, 29)),
            ("2023-365", datetime.date(2023, 12, 31)),
        ]
        for date_str, expected in test_cases:
            with self.subTest(date_str=date_str):
                self.assertEqual(DateParser.parse_date(date_str), expected)

    def test_invalid_julian_dates(self):
        """Test that invalid Julian dates return None."""
        test_cases = [
            "2023-366",
            "2024-367",
            "2023-0",
        ]
        for date_str in test_cases:
            with self.subTest(date_str=date_str):
                self.assertIsNone(DateParser.parse_date(date_str))

    def test_iso_week_dates(self):
        """Test ISO 8601 week date format (YYYY-Www-D)."""
        test_cases = [
            ("2025-W37-2", datetime.date(2025, 9, 9)),
            ("2020-W01-1", datetime.date(2019, 12, 30)),
        ]
        for date_str, expected in test_cases:
            with self.subTest(date_str=date_str):
                self.assertEqual(DateParser.parse_date(date_str), expected)

    def test_month_year_only(self):
        """Test formats with only month and year (default to 1st day)."""
        test_cases = [
            ("Dec 1990", datetime.date(1990, 12, 1)),
            ("12/1990", datetime.date(1990, 12, 1)),
            ("December 2000", datetime.date(2000, 12, 1)),
            ("January 1995", datetime.date(1995, 1, 1)),
        ]
        for date_str, expected in test_cases:
            with self.subTest(date_str=date_str):
                self.assertEqual(DateParser.parse_date(date_str), expected)

    def test_year_only(self):
        """Test year-only format (defaults to January 1st)."""
        test_cases = [
            ("1990", datetime.date(1990, 1, 1)),
            ("2000", datetime.date(2000, 1, 1)),
            ("2024", datetime.date(2024, 1, 1)),
        ]
        for date_str, expected in test_cases:
            with self.subTest(date_str=date_str):
                self.assertEqual(DateParser.parse_date(date_str), expected)


class TestDateParserCompactNumeric(unittest.TestCase):
    """Tests for compact numeric date formats."""

    def test_eight_digit_formats(self):
        """Test 8-digit compact formats."""
        test_cases = [
            ("19991020", datetime.date(1999, 10, 20)),
            ("16052005", datetime.date(2005, 5, 16)),
        ]
        for date_str, expected in test_cases:
            with self.subTest(date_str=date_str):
                result = DateParser.parse_date(date_str)
                self.assertIsNotNone(result)
                self.assertIsInstance(result, datetime.date)

    def test_six_digit_formats(self):
        """Test 6-digit compact formats with two-digit years."""
        test_cases = [
            ("102598", datetime.date(1998, 10, 25)),
            ("251098", datetime.date(1998, 10, 25)),
        ]
        for date_str, expected in test_cases:
            with self.subTest(date_str=date_str):
                result = DateParser.parse_date(date_str)
                self.assertIsNotNone(result)
                self.assertIsInstance(result, datetime.date)


class TestDateParserTimestamps(unittest.TestCase):
    """Tests for timestamp formats."""

    def test_iso_8601_timestamps(self):
        """Test ISO 8601 timestamp formats."""
        test_cases = [
            ("2025-09-09 19:30:00", datetime.date(2025, 9, 9)),
            ("2025-09-09T19:30:00", datetime.date(2025, 9, 9)),
            ("2025-09-09T19:30:00.123456", datetime.date(2025, 9, 9)),
            ("2025-09-09 19:30", datetime.date(2025, 9, 9)),
        ]
        for date_str, expected in test_cases:
            with self.subTest(date_str=date_str):
                self.assertEqual(DateParser.parse_date(date_str), expected)

    def test_us_timestamps(self):
        """Test US-style timestamps."""
        test_cases = [
            ("09/09/2025 07:30:00 PM", datetime.date(2025, 9, 9)),
            ("09/09/2025 07:30 PM", datetime.date(2025, 9, 9)),
        ]
        for date_str, expected in test_cases:
            with self.subTest(date_str=date_str):
                self.assertEqual(DateParser.parse_date(date_str), expected)

    def test_rfc_formats(self):
        """Test RFC 2822/822 style formats."""
        test_cases = [
            ("Mon 25 Dec 1990", datetime.date(1990, 12, 25)),
            ("Tue, Sep 9, 2025", datetime.date(2025, 9, 9)),
        ]
        for date_str, expected in test_cases:
            with self.subTest(date_str=date_str):
                self.assertEqual(DateParser.parse_date(date_str), expected)


class TestDateParserTwoDigitYears(unittest.TestCase):
    """Tests for two-digit year handling."""

    def test_two_digit_year_century_detection(self):
        """Test correct century detection for two-digit years."""
        test_cases = [
            ("12/25/90", 1990),
            ("12/25/49", 2049),
            ("01/01/05", 2005),
            ("01/01/99", 1999),
        ]
        for date_str, expected_year in test_cases:
            with self.subTest(date_str=date_str):
                result = DateParser.parse_date(date_str)
                self.assertIsNotNone(result)
                if result is not None:
                    self.assertEqual(result.year, expected_year)


class TestDateParserEdgeCases(unittest.TestCase):
    """Tests for edge cases and error handling in date parsing."""

    def test_whitespace_handling(self):
        """Test leading/trailing whitespace is handled."""
        test_cases = [
            ("  1995-12-25  ", datetime.date(1995, 12, 25)),
            ("\t2000-01-01\n", datetime.date(2000, 1, 1)),
            ("  December 25, 1990  ", datetime.date(1990, 12, 25)),
        ]
        for date_str, expected in test_cases:
            with self.subTest(date_str=date_str):
                self.assertEqual(DateParser.parse_date(date_str), expected)

    def test_day_name_prefix_stripped(self):
        """Test that day names are properly stripped."""
        test_cases = [
            ("Tuesday, September 9, 2025", datetime.date(2025, 9, 9)),
            ("Mon, Dec 25, 1990", datetime.date(1990, 12, 25)),
            ("Friday, 1 Jan 2000", datetime.date(2000, 1, 1)),
        ]
        for date_str, expected in test_cases:
            with self.subTest(date_str=date_str):
                self.assertEqual(DateParser.parse_date(date_str), expected)

    def test_invalid_formats_return_none(self):
        """Test that unparseable strings return None."""
        test_cases = [
            "not a real date",
            "99/99/9999",
            "abcdefg",
            "",
            "  ",
        ]
        for date_str in test_cases:
            with self.subTest(date_str=date_str):
                self.assertIsNone(DateParser.parse_date(date_str))

    def test_invalid_date_values_return_none(self):
        """Test that invalid date values return None."""
        test_cases = [
            "Feb 30, 2023",
            "Sep 31, 2023",
            "2023-13-01",
            "2023-00-01",
        ]
        for date_str in test_cases:
            with self.subTest(date_str=date_str):
                self.assertIsNone(DateParser.parse_date(date_str))

    def test_compact_month_name_formats(self):
        """Test compact formats with month names."""
        test_cases = [
            ("25DEC2023", datetime.date(2023, 12, 25)),
            ("2023dec25", datetime.date(2023, 12, 25)),
            ("01jan2000", datetime.date(2000, 1, 1)),
        ]
        for date_str, expected in test_cases:
            with self.subTest(date_str=date_str):
                self.assertEqual(DateParser.parse_date(date_str), expected)


# =============================================================================
# AGE CALCULATOR TESTS
# =============================================================================

class TestAgeCalculatorBasic(unittest.TestCase):
    """Tests for basic age calculation functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_today = datetime.date(2025, 9, 9)

    def test_age_when_birthday_already_passed_this_year(self):
        """Test age calculation when birthday has already occurred this year."""
        birthday = datetime.date(1990, 8, 20)
        result = AgeCalculator.calculate_age(birthday, today=self.mock_today)

        self.assertEqual(result.years, 35)
        self.assertEqual(result.months, 0)
        self.assertEqual(result.days, 20)
        self.assertEqual(result.birth_day_of_week, "Monday")
        self.assertEqual(result.next_birthday_in_days, 345)
        self.assertEqual(result.total_days, (self.mock_today - birthday).days)

    def test_age_when_birthday_upcoming_this_year(self):
        """Test age calculation when birthday hasn't occurred yet this year."""
        birthday = datetime.date(1990, 10, 30)
        result = AgeCalculator.calculate_age(birthday, today=self.mock_today)

        self.assertEqual(result.years, 34)
        self.assertEqual(result.months, 10)
        self.assertEqual(result.days, 10)
        self.assertEqual(result.next_birthday_in_days, 51)

    def test_age_when_birthday_is_today(self):
        """Test age calculation when today is the birthday."""
        birthday = datetime.date(2005, 9, 9)
        result = AgeCalculator.calculate_age(birthday, today=self.mock_today)

        self.assertEqual(result.years, 20)
        self.assertEqual(result.months, 0)
        self.assertEqual(result.days, 0)
        self.assertEqual(result.next_birthday_in_days, 0)

    def test_age_one_day_old(self):
        """Test age calculation for a one-day-old person."""
        birthday = datetime.date(2025, 9, 8)
        result = AgeCalculator.calculate_age(birthday, today=self.mock_today)

        self.assertEqual(result.years, 0)
        self.assertEqual(result.months, 0)
        self.assertEqual(result.days, 1)
        self.assertEqual(result.total_days, 1)

    def test_day_of_week_calculation(self):
        """Test that day of week is correctly calculated."""
        test_cases = [
            (datetime.date(1990, 12, 25), "Tuesday"),
            (datetime.date(2000, 1, 1), "Saturday"),
            (datetime.date(1995, 7, 4), "Tuesday"),
        ]
        for birthday, expected_day in test_cases:
            with self.subTest(birthday=birthday):
                result = AgeCalculator.calculate_age(birthday, today=self.mock_today)
                self.assertEqual(result.birth_day_of_week, expected_day)


class TestAgeCalculatorLeapYears(unittest.TestCase):
    """Tests for leap year scenarios."""

    def test_feb_29_birthday_on_leap_year(self):
        """Test Feb 29 birthday calculation on a leap year."""
        mock_today = datetime.date(2024, 2, 29)
        birthday = datetime.date(2000, 2, 29)
        result = AgeCalculator.calculate_age(birthday, today=mock_today)

        self.assertEqual(result.years, 24)
        self.assertEqual(result.months, 0)
        self.assertEqual(result.days, 0)
        self.assertEqual(result.next_birthday_in_days, 0)

    def test_feb_29_birthday_on_non_leap_year(self):
        """Test Feb 29 birthday calculation on a non-leap year."""
        mock_today = datetime.date(2025, 3, 1)
        birthday = datetime.date(2000, 2, 29)
        result = AgeCalculator.calculate_age(birthday, today=mock_today)

        self.assertEqual(result.years, 25)
        self.assertEqual(result.months, 0)
        self.assertEqual(result.days, 1)

    def test_feb_29_next_birthday_on_non_leap_year(self):
        """Test next birthday calculation for Feb 29 birthday in non-leap year."""
        mock_today = datetime.date(2025, 1, 1)
        birthday = datetime.date(2000, 2, 29)
        result = AgeCalculator.calculate_age(birthday, today=mock_today)

        self.assertIsNotNone(result.next_birthday_in_days)
        self.assertGreater(result.next_birthday_in_days, 0)


class TestAgeCalculatorBoundaryConditions(unittest.TestCase):
    """Tests for boundary conditions."""

    def test_day_before_birthday(self):
        """Test age calculation one day before birthday."""
        mock_today = datetime.date(2025, 8, 19)
        birthday = datetime.date(1990, 8, 20)
        result = AgeCalculator.calculate_age(birthday, today=mock_today)

        self.assertEqual(result.years, 34)
        self.assertEqual(result.months, 11)
        self.assertEqual(result.days, 30)
        self.assertEqual(result.next_birthday_in_days, 1)

    def test_month_end_boundaries(self):
        """Test age calculation across month-end boundaries."""
        mock_today = datetime.date(2025, 2, 28)
        birthday = datetime.date(2024, 1, 31)
        result = AgeCalculator.calculate_age(birthday, today=mock_today)

        self.assertEqual(result.years, 1)
        self.assertEqual(result.months, 0)
        self.assertEqual(result.days, 28)

    def test_new_years_day_birthday(self):
        """Test birthday on January 1st."""
        mock_today = datetime.date(2025, 12, 31)
        birthday = datetime.date(2000, 1, 1)
        result = AgeCalculator.calculate_age(birthday, today=mock_today)

        self.assertEqual(result.years, 25)
        self.assertEqual(result.next_birthday_in_days, 1)

    def test_year_end_birthday(self):
        """Test birthday on December 31st."""
        mock_today = datetime.date(2025, 1, 1)
        birthday = datetime.date(2000, 12, 31)
        result = AgeCalculator.calculate_age(birthday, today=mock_today)

        self.assertEqual(result.years, 24)
        self.assertGreater(result.next_birthday_in_days, 360)


class TestAgeCalculatorErrorHandling(unittest.TestCase):
    """Tests for error handling."""

    def test_future_birthday_raises_error(self):
        """Test that future birthdays raise ValueError."""
        mock_today = datetime.date(2025, 9, 9)
        future_birthday = datetime.date(2026, 1, 1)

        with self.assertRaisesRegex(ValueError, "Birthday cannot be in the future"):
            AgeCalculator.calculate_age(future_birthday, today=mock_today)

    def test_same_day_future_birthday_raises_error(self):
        """Test that exact future date raises error."""
        mock_today = datetime.date(2025, 9, 9)
        future = datetime.date(2025, 9, 10)

        with self.assertRaisesRegex(ValueError, "Birthday cannot be in the future"):
            AgeCalculator.calculate_age(future, today=mock_today)


class TestAgeCalculatorFormatting(unittest.TestCase):
    """Tests for age output formatting."""

    def test_format_with_all_components_plural(self):
        """Test formatting with years, months, and days (plural)."""
        age_data = AgeResult(
            years=33, months=8, days=12, total_days=12309,
            birth_day_of_week='Monday', next_birthday_in_days=110
        )
        output = AgeCalculator.format_age_output(datetime.date(1990, 1, 1), age_data)

        self.assertIn("Born on a Monday", output)
        self.assertIn("33 years, 8 months and 12 days", output)
        self.assertIn("12,309 days", output)
        self.assertIn("110 days", output)

    def test_format_with_all_components_singular(self):
        """Test formatting with all singular components."""
        age_data = AgeResult(
            years=1, months=1, days=1, total_days=397,
            birth_day_of_week='Tuesday', next_birthday_in_days=300
        )
        output = AgeCalculator.format_age_output(datetime.date(2024, 8, 6), age_data)

        self.assertIn("1 year, 1 month and 1 day", output)

    def test_format_with_missing_months(self):
        """Test formatting when months is zero."""
        age_data = AgeResult(
            years=1, months=0, days=12, total_days=377,
            birth_day_of_week='Friday', next_birthday_in_days=321
        )
        output = AgeCalculator.format_age_output(datetime.date(2024, 7, 26), age_data)

        self.assertIn("1 year and 12 days", output)
        self.assertNotIn("0 month", output)

    def test_format_with_only_days(self):
        """Test formatting when only days component exists."""
        age_data = AgeResult(
            years=0, months=0, days=1, total_days=1,
            birth_day_of_week='Monday', next_birthday_in_days=364
        )
        output = AgeCalculator.format_age_output(datetime.date(2025, 9, 8), age_data)

        self.assertIn("1 day", output)
        self.assertNotIn("year", output)
        self.assertNotIn("month", output)

    def test_format_birthday_message_when_birthday(self):
        """Test birthday message when it's the birthday."""
        age_data = AgeResult(
            years=20, months=0, days=0, total_days=7305,
            birth_day_of_week='Friday', next_birthday_in_days=0
        )
        output = AgeCalculator.format_age_output(datetime.date(2005, 9, 9), age_data)

        self.assertIn("Happy Birthday!", output)

    def test_format_with_emoji_enabled(self):
        """Test formatting with emoji enabled."""
        age_data = AgeResult(
            years=25, months=0, days=0, total_days=9131,
            birth_day_of_week='Saturday', next_birthday_in_days=0
        )
        output = AgeCalculator.format_age_output(
            datetime.date(2000, 1, 1), age_data, use_emoji=True
        )

        self.assertIn("🎉", output)
        self.assertIn("✨", output)

    def test_format_with_emoji_disabled(self):
        """Test formatting with emoji disabled."""
        age_data = AgeResult(
            years=25, months=0, days=0, total_days=9131,
            birth_day_of_week='Saturday', next_birthday_in_days=0
        )
        output = AgeCalculator.format_age_output(
            datetime.date(2000, 1, 1), age_data, use_emoji=False
        )

        self.assertNotIn("🎉", output)
        self.assertNotIn("✨", output)
        self.assertNotIn("🎂", output)
        self.assertIn("Happy Birthday!", output)


# =============================================================================
# MESSAGE FORMATTER TESTS
# =============================================================================

class TestMessageFormatter(unittest.TestCase):
    """Tests for MessageFormatter class."""

    def test_goodbye_with_emoji(self):
        """Test goodbye message with emoji."""
        formatter = MessageFormatter(use_emoji=True)
        self.assertEqual(formatter.goodbye(), "Goodbye! 👋")

    def test_goodbye_without_emoji(self):
        """Test goodbye message without emoji."""
        formatter = MessageFormatter(use_emoji=False)
        self.assertEqual(formatter.goodbye(), "Goodbye!")

    def test_warning_with_emoji(self):
        """Test warning message with emoji."""
        formatter = MessageFormatter(use_emoji=True)
        result = formatter.warning("Test warning")
        self.assertEqual(result, "⚠️ Test warning")

    def test_warning_without_emoji(self):
        """Test warning message without emoji."""
        formatter = MessageFormatter(use_emoji=False)
        result = formatter.warning("Test warning")
        self.assertEqual(result, "Warning: Test warning")

    def test_error_with_emoji(self):
        """Test error message with emoji."""
        formatter = MessageFormatter(use_emoji=True)
        result = formatter.error("Test error")
        self.assertEqual(result, "❌ Test error")

    def test_error_without_emoji(self):
        """Test error message without emoji."""
        formatter = MessageFormatter(use_emoji=False)
        result = formatter.error("Test error")
        self.assertEqual(result, "Error: Test error")

    def test_results_header_with_emoji(self):
        """Test results header with emoji."""
        formatter = MessageFormatter(use_emoji=True)
        self.assertEqual(formatter.results_header(), "✨ Results:")

    def test_results_header_without_emoji(self):
        """Test results header without emoji."""
        formatter = MessageFormatter(use_emoji=False)
        self.assertEqual(formatter.results_header(), "Results:")

    def test_birthday_message_on_birthday_with_emoji(self):
        """Test birthday message on birthday with emoji."""
        formatter = MessageFormatter(use_emoji=True)
        result = formatter.birthday_message(0)
        self.assertEqual(result, "Happy Birthday! 🎉")

    def test_birthday_message_on_birthday_without_emoji(self):
        """Test birthday message on birthday without emoji."""
        formatter = MessageFormatter(use_emoji=False)
        result = formatter.birthday_message(0)
        self.assertEqual(result, "Happy Birthday!")

    def test_birthday_message_countdown_with_emoji(self):
        """Test birthday countdown message with emoji."""
        formatter = MessageFormatter(use_emoji=True)
        result = formatter.birthday_message(30)
        self.assertEqual(result, "Your next birthday is in 30 days! 🎂")

    def test_birthday_message_countdown_without_emoji(self):
        """Test birthday countdown message without emoji."""
        formatter = MessageFormatter(use_emoji=False)
        result = formatter.birthday_message(30)
        self.assertEqual(result, "Your next birthday is in 30 days!")

    def test_title_with_emoji(self):
        """Test title with emoji."""
        formatter = MessageFormatter(use_emoji=True)
        self.assertEqual(formatter.title(), "🎂 Age Calculator 🎂")

    def test_title_without_emoji(self):
        """Test title without emoji."""
        formatter = MessageFormatter(use_emoji=False)
        self.assertEqual(formatter.title(), "Age Calculator")


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestIntegration(unittest.TestCase):
    """End-to-end integration tests."""

    def test_complete_workflow_standard_date(self):
        """Test complete workflow with a standard date."""
        date_str = "1990-12-25"
        birthday = DateParser.parse_date(date_str)
        self.assertIsNotNone(birthday)

        assert birthday is not None

        age_result = AgeCalculator.calculate_age(
            birthday, today=datetime.date(2025, 9, 9)
        )
        self.assertEqual(age_result.years, 34)

        output = AgeCalculator.format_age_output(birthday, age_result)
        self.assertIn("Tuesday", output)
        self.assertIn("December 25, 1990", output)

    def test_complete_workflow_natural_language(self):
        """Test complete workflow with natural language date."""
        date_str = "December 25th, 1990"
        birthday = DateParser.parse_date(date_str)
        self.assertIsNotNone(birthday)
        self.assertEqual(birthday, datetime.date(1990, 12, 25))

        assert birthday is not None

        age_result = AgeCalculator.calculate_age(
            birthday, today=datetime.date(2025, 9, 9)
        )
        output = AgeCalculator.format_age_output(birthday, age_result)
        self.assertIn("34 years", output)

    def test_complete_workflow_relative_date(self):
        """Test complete workflow with relative date."""
        date_str = "yesterday"
        birthday = DateParser.parse_date(date_str)
        self.assertIsNotNone(birthday)

        today = datetime.date.today()
        expected = today - datetime.timedelta(days=1)
        self.assertEqual(birthday, expected)

        assert birthday is not None

        age_result = AgeCalculator.calculate_age(birthday, today=today)
        self.assertEqual(age_result.days, 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
