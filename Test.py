import unittest
import datetime
from unittest.mock import patch

from age_calculator import DateParser, AgeCalculator, AgeResult

class TestDateParserStandardFormats(unittest.TestCase):
    """Tests for standard, unambiguous date formats."""

    def test_parses_yyyy_mm_dd(self):
        expected = datetime.date(1995, 12, 25)
        self.assertEqual(DateParser.parse_date("1995-12-25"), expected)

    def test_parses_mm_dd_yyyy(self):
        expected = datetime.date(1995, 12, 25)
        self.assertEqual(DateParser.parse_date("12/25/1995"), expected)

    def test_parses_dd_mm_yyyy(self):
        expected = datetime.date(1995, 12, 25)
        self.assertEqual(DateParser.parse_date("25.12.1995"), expected)

class TestDateParserNaturalLanguage(unittest.TestCase):
    """Tests for natural language date formats."""

    def test_parses_full_month_day_year(self):
        expected = datetime.date(2001, 1, 15)
        self.assertEqual(DateParser.parse_date("January 15, 2001"), expected)

    def test_parses_abbr_month_day_year(self):
        expected = datetime.date(2001, 1, 15)
        self.assertEqual(DateParser.parse_date("15 Jan 2001"), expected)

    def test_parses_day_with_ordinal_indicator(self):
        expected = datetime.date(2001, 1, 15)
        self.assertEqual(DateParser.parse_date("15th January, 2001"), expected)
        
    def test_parses_month_first_with_ordinal_indicator(self):
        expected = datetime.date(2000, 12, 1)
        self.assertEqual(DateParser.parse_date("December 1st, 2000"), expected)

    def test_handles_mixed_case(self):
        expected = datetime.date(2001, 1, 15)
        self.assertEqual(DateParser.parse_date("jAnUaRy 15, 2001"), expected)

class TestDateParserSpecialFormats(unittest.TestCase):
    """Tests for newly added special date formats like Julian and 'day of'."""

    def test_parses_day_of_month_format(self):
        """Tests format like '25 of December 2005'."""
        expected = datetime.date(2005, 12, 25)
        self.assertEqual(DateParser.parse_date("25 of December 2005"), expected)
        self.assertEqual(DateParser.parse_date("1 of Jan 2001"), datetime.date(2001, 1, 1))

    def test_parses_julian_date_format(self):
        """Tests YYYY-DDD format."""
        self.assertEqual(DateParser.parse_date("2023-359"), datetime.date(2023, 12, 25))
        self.assertEqual(DateParser.parse_date("2024-1"), datetime.date(2024, 1, 1))
        self.assertEqual(DateParser.parse_date("2024-60"), datetime.date(2024, 2, 29))

    def test_returns_none_for_invalid_julian_date(self):
        """Julian day number cannot exceed the number of days in the year."""
        self.assertIsNone(DateParser.parse_date("2023-366"))
        self.assertIsNone(DateParser.parse_date("2024-367"))

class TestDateParserCompactNumericFormats(unittest.TestCase):
    """Tests for compact, all-numeric date formats."""

    def test_parses_yyyymmdd(self):
        self.assertEqual(DateParser.parse_date("19991020"), datetime.date(1999, 10, 20))

    def test_parses_ddmmyyyy(self):
        self.assertEqual(DateParser.parse_date("16052005"), datetime.date(2005, 5, 16))

    def test_parses_mmddyy(self):
        self.assertEqual(DateParser.parse_date("102598"), datetime.date(1998, 10, 25))

    def test_parses_ddmmyy(self):
        self.assertEqual(DateParser.parse_date("251098"), datetime.date(1998, 10, 25))

class TestDateParserRelativeDates(unittest.TestCase):
    """Tests for relative date strings like 'today' or 'yesterday'."""

    def test_parses_today(self):
        self.assertEqual(DateParser.parse_date("today"), datetime.date.today())

    def test_parses_yesterday(self):
        expected = datetime.date.today() - datetime.timedelta(days=1)
        self.assertEqual(DateParser.parse_date("yesterday"), expected)

    def test_parses_tomorrow(self):
        expected = datetime.date.today() + datetime.timedelta(days=1)
        self.assertEqual(DateParser.parse_date("tomorrow"), expected)

class TestDateParserAmbiguousAndEdgeCases(unittest.TestCase):
    """Tests for ambiguous formats and other edge cases."""

    def test_handles_two_digit_years(self):
        """Test correct century detection for two-digit years."""
        self.assertEqual(DateParser.parse_date("12/25/90"), datetime.date(1990, 12, 25))
        self.assertEqual(DateParser.parse_date("01/01/05"), datetime.date(2005, 1, 1))

    def test_handles_month_year_only(self):
        """Formats with only month and year should default to the 1st day."""
        expected = datetime.date(1990, 12, 1)
        self.assertEqual(DateParser.parse_date("Dec 1990"), expected)
        self.assertEqual(DateParser.parse_date("12/1990"), expected)

    def test_handles_leading_trailing_whitespace(self):
        expected = datetime.date(1995, 12, 25)
        self.assertEqual(DateParser.parse_date("  1995-12-25  "), expected)

    def test_returns_none_for_invalid_formats(self):
        self.assertIsNone(DateParser.parse_date("not a real date"))
        self.assertIsNone(DateParser.parse_date("99/99/9999"))
        self.assertIsNone(DateParser.parse_date("12345"))

    def test_returns_none_for_invalid_date_values(self):
        self.assertIsNone(DateParser.parse_date("Feb 30, 2023"))
        self.assertIsNone(DateParser.parse_date("Sep 31, 2023"))

class TestDateParserComprehensiveFormats(unittest.TestCase):
    """Tests for additional formats like day names, ISO week dates, and timestamps."""

    def test_parses_date_with_full_day_name(self):
        expected = datetime.date(2025, 9, 9)
        self.assertEqual(DateParser.parse_date("Tuesday, September 9, 2025"), expected)
        self.assertEqual(DateParser.parse_date("Tue, Sep 9, 2025"), expected)

    def test_parses_iso_week_date(self):
        # Tuesday, Sep 9, 2025 is the 2nd day of the 37th week of 2025.
        expected = datetime.date(2025, 9, 9)
        self.assertEqual(DateParser.parse_date("2025-W37-2"), expected)

    def test_parses_date_with_time_component(self):
        """Time components should be successfully parsed but ignored."""
        expected = datetime.date(2025, 9, 9)
        self.assertEqual(DateParser.parse_date("2025-09-09 19:30:00"), expected)
        self.assertEqual(DateParser.parse_date("09/09/2025 07:30:00 PM"), expected)

    def test_parses_date_with_t_separator(self):
        """The 'T' separator in timestamps should be handled."""
        expected = datetime.date(2025, 9, 9)
        self.assertEqual(DateParser.parse_date("2025-09-09T19:30:00"), expected)

    def test_parses_compact_month_name_format(self):
        expected = datetime.date(2023, 12, 25)
        self.assertEqual(DateParser.parse_date("25DEC2023"), expected)
        self.assertEqual(DateParser.parse_date("2023dec25"), expected)

class TestAgeCalculatorCoreFunctionality(unittest.TestCase):
    """Tests the basic age calculation logic."""

    def setUp(self):
        self.mock_today = datetime.date(2025, 9, 9)

    def test_calculates_age_birthday_passed(self):
        birthday = datetime.date(1990, 8, 20) # A Monday
        age_result = AgeCalculator.calculate_age(birthday, today=self.mock_today)
        self.assertEqual(age_result.years, 35)
        self.assertEqual(age_result.months, 0)
        self.assertEqual(age_result.days, 20)
        self.assertEqual(age_result.birth_day_of_week, "Monday")
        self.assertEqual(age_result.next_birthday_in_days, 345)

    def test_calculates_age_birthday_upcoming(self):
        birthday = datetime.date(1990, 10, 30)
        age_result = AgeCalculator.calculate_age(birthday, today=self.mock_today)
        self.assertEqual(age_result.years, 34)
        self.assertEqual(age_result.months, 10)
        self.assertEqual(age_result.days, 10)
        self.assertEqual(age_result.next_birthday_in_days, 51)

    def test_calculates_age_birthday_is_today(self):
        birthday = datetime.date(2005, 9, 9)
        age_result = AgeCalculator.calculate_age(birthday, today=self.mock_today)
        self.assertEqual(age_result.years, 20)
        self.assertEqual(age_result.months, 0)
        self.assertEqual(age_result.days, 0)
        self.assertEqual(age_result.next_birthday_in_days, 0)

class TestAgeCalculatorLeapYearScenarios(unittest.TestCase):
    """Tests specifically related to leap years and Feb 29th birthdays."""

    def test_age_for_leap_birthday_on_leap_year_date(self):
        mock_today = datetime.date(2024, 2, 29)
        birthday = datetime.date(2000, 2, 29)
        age_result = AgeCalculator.calculate_age(birthday, today=mock_today)
        self.assertEqual(age_result.years, 24)
        self.assertEqual(age_result.months, 0)
        self.assertEqual(age_result.days, 0)

    def test_age_for_leap_birthday_on_common_year_after_feb(self):
        mock_today = datetime.date(2025, 3, 1)
        birthday = datetime.date(2000, 2, 29)
        age_result = AgeCalculator.calculate_age(birthday, today=mock_today)
        self.assertEqual(age_result.years, 25)
        self.assertEqual(age_result.months, 0)
        self.assertEqual(age_result.days, 1)

class TestAgeCalculatorBoundaryConditions(unittest.TestCase):
    """Tests for edge cases around month and year boundaries."""

    def test_age_on_day_before_birthday(self):
        mock_today = datetime.date(2025, 8, 19)
        birthday = datetime.date(1990, 8, 20)
        age_result = AgeCalculator.calculate_age(birthday, today=mock_today)
        self.assertEqual(age_result.years, 34)
        self.assertEqual(age_result.months, 11)
        self.assertEqual(age_result.days, 30)

    def test_age_on_month_end_boundary(self):
        mock_today = datetime.date(2025, 2, 28)
        birthday = datetime.date(2024, 1, 31)
        age_result = AgeCalculator.calculate_age(birthday, today=mock_today)
        self.assertEqual(age_result.years, 1)
        self.assertEqual(age_result.months, 0)
        self.assertEqual(age_result.days, 28)

class TestAgeCalculatorOutputFormatting(unittest.TestCase):
    """Tests the new, enhanced formatted string output."""

    def test_formats_full_age_plural(self):
        age_data = AgeResult(years=33, months=8, days=12, total_days=12309, birth_day_of_week='Monday', next_birthday_in_days=110)
        output = AgeCalculator.format_age_output(datetime.date(1990, 1, 1), age_data)
        self.assertIn("Born on a Monday", output)
        self.assertIn("You are 33 years, 8 months and 12 days old.", output)
        self.assertIn("That's a total of 12,309 days!", output)
        self.assertIn("Your next birthday is in 110 days!", output)

    def test_formats_full_age_singular(self):
        age_data = AgeResult(years=1, months=1, days=1, total_days=397, birth_day_of_week='Tuesday', next_birthday_in_days=300)
        output = AgeCalculator.format_age_output(datetime.date(2024, 8, 6), age_data)
        self.assertIn("You are 1 year, 1 month and 1 day old.", output)

    def test_formats_age_with_zero_months(self):
        age_data = AgeResult(years=1, months=0, days=12, total_days=377, birth_day_of_week='Friday', next_birthday_in_days=321)
        output = AgeCalculator.format_age_output(datetime.date(2024, 7, 26), age_data)
        self.assertIn("You are 1 year and 12 days old.", output)

    def test_formats_age_with_only_days(self):
        age_data = AgeResult(years=0, months=0, days=1, total_days=1, birth_day_of_week='Monday', next_birthday_in_days=364)
        output = AgeCalculator.format_age_output(datetime.date(2025, 9, 8), age_data)
        self.assertIn("You are 1 day old.", output)
    
    def test_formats_happy_birthday_message(self):
        """Tests the special message for today's birthday."""
        age_data = AgeResult(years=20, months=0, days=0, total_days=7305, birth_day_of_week='Friday', next_birthday_in_days=0)
        output = AgeCalculator.format_age_output(datetime.date(2005, 9, 9), age_data)
        self.assertIn("Happy Birthday! 🎉", output)

class TestAgeCalculatorErrorHandling(unittest.TestCase):
    """Tests the error handling for invalid inputs."""

    def test_raises_value_error_for_future_birthday(self):
        mock_today = datetime.date(2025, 9, 9)
        future_birthday = datetime.date(2026, 1, 1)
        with self.assertRaisesRegex(ValueError, "Birthday cannot be in the future."):
            AgeCalculator.calculate_age(future_birthday, today=mock_today)

if __name__ == '__main__':
    unittest.main(verbosity=2)
