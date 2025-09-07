import unittest
import datetime
from unittest.mock import patch

from age_calculator import DateParser, AgeCalculator

# --- Test Suites for DateParser ---

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
        """Unparseable strings should return None."""
        self.assertIsNone(DateParser.parse_date("not a real date"))
        self.assertIsNone(DateParser.parse_date("99/99/9999"))
        self.assertIsNone(DateParser.parse_date("12345"))

    def test_returns_none_for_invalid_date_values(self):
        """Strings with impossible date values should return None."""
        self.assertIsNone(DateParser.parse_date("Feb 30, 2023"))
        self.assertIsNone(DateParser.parse_date("Sep 31, 2023"))

# --- Test Suites for AgeCalculator ---

class TestAgeCalculatorCoreFunctionality(unittest.TestCase):
    """Tests the basic age calculation logic."""

    def setUp(self):
        """Set a fixed 'today' for all tests in this class."""
        self.mock_today = datetime.date(2025, 9, 7)

    def test_calculates_age_birthday_passed(self):
        """Test a straightforward case where the birthday has passed this year."""
        birthday = datetime.date(1990, 8, 20)
        age_data = AgeCalculator.calculate_age(birthday, today=self.mock_today)
        self.assertEqual(age_data['years'], 35)
        self.assertEqual(age_data['months'], 0)
        self.assertEqual(age_data['days'], 18)

    def test_calculates_age_birthday_upcoming(self):
        """Test a straightforward case where the birthday is later in the year."""
        birthday = datetime.date(1990, 10, 30)
        age_data = AgeCalculator.calculate_age(birthday, today=self.mock_today)
        self.assertEqual(age_data['years'], 34)
        self.assertEqual(age_data['months'], 10)
        self.assertEqual(age_data['days'], 8)

    def test_calculates_age_birthday_is_today(self):
        """Test the case where the birthday is the same as the current date."""
        birthday = datetime.date(2005, 9, 7)
        age_data = AgeCalculator.calculate_age(birthday, today=self.mock_today)
        self.assertEqual(age_data['years'], 20)
        self.assertEqual(age_data['months'], 0)
        self.assertEqual(age_data['days'], 0)

    def test_calculates_age_less_than_one_month(self):
        """Test for an age of only a few days."""
        birthday = datetime.date(2025, 9, 4)
        age_data = AgeCalculator.calculate_age(birthday, today=self.mock_today)
        self.assertEqual(age_data['years'], 0)
        self.assertEqual(age_data['months'], 0)
        self.assertEqual(age_data['days'], 3)

    def test_calculates_age_less_than_one_year(self):
        """Test for an age of several months but less than a full year."""
        birthday = datetime.date(2025, 3, 15)
        age_data = AgeCalculator.calculate_age(birthday, today=self.mock_today)
        self.assertEqual(age_data['years'], 0)
        self.assertEqual(age_data['months'], 5)
        self.assertEqual(age_data['days'], 23)

class TestAgeCalculatorLeapYearScenarios(unittest.TestCase):
    """Tests specifically related to leap years and Feb 29th birthdays."""

    def test_age_for_leap_birthday_on_leap_year_date(self):
        """Test age for a leap birthday when today is also a leap day."""
        mock_today = datetime.date(2024, 2, 29)
        birthday = datetime.date(2000, 2, 29)
        age_data = AgeCalculator.calculate_age(birthday, today=mock_today)
        self.assertEqual(age_data['years'], 24)
        self.assertEqual(age_data['months'], 0)
        self.assertEqual(age_data['days'], 0)

    def test_age_for_leap_birthday_on_common_year_after_feb(self):
        """Test age for a leap birthday in a non-leap year (after Feb)."""
        mock_today = datetime.date(2025, 3, 1)
        birthday = datetime.date(2000, 2, 29)
        age_data = AgeCalculator.calculate_age(birthday, today=mock_today)
        self.assertEqual(age_data['years'], 25)
        self.assertEqual(age_data['months'], 0)
        self.assertEqual(age_data['days'], 1)

    def test_age_for_leap_birthday_on_common_year_before_feb(self):
        """Test age for a leap birthday in a non-leap year (before Feb)."""
        mock_today = datetime.date(2025, 2, 1)
        birthday = datetime.date(2000, 2, 29)
        age_data = AgeCalculator.calculate_age(birthday, today=mock_today)
        self.assertEqual(age_data['years'], 24)
        self.assertEqual(age_data['months'], 11)
        self.assertEqual(age_data['days'], 3)

class TestAgeCalculatorBoundaryConditions(unittest.TestCase):
    """Tests for edge cases around month and year boundaries."""

    def test_age_on_day_before_birthday(self):
        """Test the age calculation on the day immediately before a birthday."""
        mock_today = datetime.date(2025, 8, 19)
        birthday = datetime.date(1990, 8, 20)
        age_data = AgeCalculator.calculate_age(birthday, today=mock_today)
        self.assertEqual(age_data['years'], 34)
        self.assertEqual(age_data['months'], 11)
        self.assertEqual(age_data['days'], 30)

    def test_age_on_month_end_boundary(self):
        """Test age calculation when birthday is on a month end (e.g., Jan 31st)."""
        mock_today = datetime.date(2025, 2, 28)
        birthday = datetime.date(2024, 1, 31)
        age_data = AgeCalculator.calculate_age(birthday, today=mock_today)
        self.assertEqual(age_data['years'], 1)
        self.assertEqual(age_data['months'], 0)
        self.assertEqual(age_data['days'], 28)

class TestAgeCalculatorOutputFormatting(unittest.TestCase):
    """Tests the formatted string output."""

    def test_formats_full_age_plural(self):
        """Test format for years, months, and days (plural)."""
        age_data = {'years': 33, 'months': 8, 'days': 12, 'total_days': 12309}
        output = AgeCalculator.format_age_output(datetime.date(1990, 1, 1), age_data)
        self.assertIn("You are 33 years, 8 months and 12 days old.", output)
        self.assertIn("That's a total of 12,309 days!", output)

    def test_formats_full_age_singular(self):
        """Test format for 1 year, 1 month, 1 day."""
        age_data = {'years': 1, 'months': 1, 'days': 1, 'total_days': 397}
        output = AgeCalculator.format_age_output(datetime.date(2024, 8, 6), age_data)
        self.assertIn("You are 1 year, 1 month and 1 day old.", output)

    def test_formats_age_with_zero_months(self):
        age_data = {'years': 1, 'months': 0, 'days': 12, 'total_days': 377}
        output = AgeCalculator.format_age_output(datetime.date(2024, 7, 26), age_data)
        self.assertIn("You are 1 year and 12 days old.", output)

    def test_formats_age_with_zero_days(self):
        age_data = {'years': 1, 'months': 1, 'days': 0, 'total_days': 396}
        output = AgeCalculator.format_age_output(datetime.date(2024, 8, 7), age_data)
        self.assertIn("You are 1 year and 1 month old.", output)

    def test_formats_age_with_zero_months_and_days(self):
        age_data = {'years': 1, 'months': 0, 'days': 0, 'total_days': 366}
        output = AgeCalculator.format_age_output(datetime.date(2024, 9, 7), age_data)
        self.assertIn("You are 1 year old.", output)

    def test_formats_age_with_zero_years(self):
        age_data = {'years': 0, 'months': 6, 'days': 6, 'total_days': 189}
        output = AgeCalculator.format_age_output(datetime.date(2025, 3, 1), age_data)
        self.assertIn("You are 6 months and 6 days old.", output)

    def test_formats_age_with_only_days(self):
        age_data = {'years': 0, 'months': 0, 'days': 1, 'total_days': 1}
        output = AgeCalculator.format_age_output(datetime.date(2025, 9, 6), age_data)
        self.assertIn("You are 1 day old.", output)

    def test_formats_age_for_newborn(self):
        """Test format for a 0-day old."""
        age_data = {'years': 0, 'months': 0, 'days': 0, 'total_days': 0}
        output = AgeCalculator.format_age_output(datetime.date(2025, 9, 7), age_data)
        self.assertIn("You are 0 days old.", output)

class TestAgeCalculatorErrorHandling(unittest.TestCase):
    """Tests the error handling for invalid inputs."""

    def test_raises_value_error_for_future_birthday(self):
        """A birthday in the future should raise a ValueError."""
        mock_today = datetime.date(2025, 9, 7)
        future_birthday = datetime.date(2026, 1, 1)
        with self.assertRaisesRegex(ValueError, "Birthday cannot be in the future."):
            AgeCalculator.calculate_age(future_birthday, today=mock_today)

if __name__ == '__main__':
    unittest.main(verbosity=2)