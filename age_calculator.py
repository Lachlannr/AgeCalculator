#!/usr/bin/env python3

"""
Age Calculator - A tool for calculating ages from various date formats.

Supports 100+ international date formats, accurate age calculation with leap year
handling, and both CLI and programmatic interfaces. Includes input validation and
bounds checking for security.
"""

import argparse
import datetime
import re
from calendar import isleap
from dataclasses import dataclass
from typing import List, Optional

DAY_NAME_REGEX = re.compile(
    r"^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|Mon|Tue|Wed|Thu|Fri|Sat|Sun),?\s*",
    re.IGNORECASE,
)
ORDINAL_SUFFIX_REGEX = re.compile(r"(\d{1,2})(st|nd|rd|th)", re.IGNORECASE)
DAY_OF_MONTH_REGEX = re.compile(
    r"(\d{1,2})(?:st|nd|rd|th)?\s+of\s+([a-zA-Z]+)\s+(\d{4})",
    re.IGNORECASE,
)
COMPACT_DATE_REGEX = re.compile(r"^\d{6,8}$")
JULIAN_DATE_REGEX = re.compile(r"^(\d{4})-(\d{1,3})$")
UNIX_TIMESTAMP_REGEX = re.compile(r"^(0|\d{9,10})$")
EXCEL_SERIAL_REGEX = re.compile(r"^\d{1,7}$")
FISCAL_QUARTER_REGEX = re.compile(r"^(\d{4})[-\s]?Q([1-4])$", re.IGNORECASE)

MAX_INPUT_LENGTH = 1000
MIN_VALID_YEAR = 1900
MAX_VALID_YEAR = 2100


@dataclass
class AgeResult:
    """Container for age calculation results including years, months, days, and additional metadata."""

    years: int
    months: int
    days: int
    total_days: int
    birth_day_of_week: str
    next_birthday_in_days: int


class DateParser:
    """Parses dates from various formats including ISO, natural language, and specialized formats."""

    DATE_FORMATS: List[str] = [
        # ISO 8601 Standard Formats (YYYY-MM-DD)
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%Y.%m.%d",
        "%Y %m %d",
        # US Date Formats (MM/DD/YYYY)
        "%m/%d/%Y",
        "%m-%d-%Y",
        "%m.%d.%Y",
        "%m %d %Y",
        # European Date Formats (DD/MM/YYYY)
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%d.%m.%Y",
        "%d %m %Y",
        # Natural Language Formats - Full Month Names
        "%B %d, %Y",
        "%b %d, %Y",
        "%d %B, %Y",
        "%d %b, %Y",
        "%B %d %Y",
        "%b %d %Y",
        "%d %B %Y",
        "%d %b %Y",
        "%d-%B-%Y",
        "%d-%b-%Y",
        "%B-%d-%Y",
        "%b-%d-%Y",
        "%Y %B %d",
        "%Y %b %d",
        "%Y, %B %d",
        "%Y, %b %d",
        # Two-Digit Year Formats
        "%m/%d/%y",
        "%m-%d-%y",
        "%m.%d.%y",
        "%d/%m/%y",
        "%d-%m-%y",
        "%d.%m.%y",
        "%y/%m/%d",
        "%y-%m-%d",
        "%y.%m.%d",
        "%m %d %y",
        "%d %m %y",
        "%y %m %d",
        # ISO Week Date Format
        "%G-W%V-%u",
        # Timestamp Formats - ISO 8601
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%d %H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M",
        "%Y/%m/%d %H:%M:%S",
        # Timestamp Formats - US Style
        "%m/%d/%Y %I:%M:%S %p",
        "%m/%d/%Y %I:%M %p",
        # Timestamp Formats - European Style
        "%d-%m-%Y %H:%M:%S",
        "%d-%m-%Y %H:%M",
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y %H:%M",
        # Timestamp Formats - RFC Style
        "%a, %d %b %Y %H:%M:%S",
        "%a %b %d %H:%M:%S %Y",
        "%a %d %b %Y",
        # Month/Year Only Formats
        "%B %Y",
        "%b %Y",
        "%Y-%m",
        "%m/%Y",
        "%m-%Y",
        "%m.%Y",
        "%Y %B",
        "%Y %b",
        "%B, %Y",
        # Compact Numeric Formats
        "%d%b%Y",
        "%Y%b%d",
        "%d%m%Y",
        "%Y%m%d",
        # International Formats - CJK (Chinese/Japanese/Korean)
        "%Y年%m月%d日",
        "%Y년 %m월 %d일",
        # International Formats - European Variations
        "%d %B %Y г.",
        "%d de %B de %Y",
        "%d. %B %Y",
        "%d %b. %Y",
        "%d de %b de %Y",
        "%d. %b %Y",
        # Database and Log File Formats
        "%Y-%m-%d %H:%M:%S.%f+00:00",
        "%Y%m%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y%m%d%H%M%S",
        "%d/%b/%Y:%H:%M:%S",
        "%Y-%m-%d %H:%M:%S,%f",
        "%d.%m.%Y %H:%M:%S",
        "%Y/%m/%d %H:%M",
        # Year Only
        "%Y",
    ]

    NATURAL_FORMATS: List[str] = [
        "%B %d, %Y",
        "%b %d, %Y",
        "%d %B, %Y",
        "%d %b, %Y",
        "%B %d %Y",
        "%b %d %Y",
        "%d %B %Y",
        "%d %b %Y",
    ]

    @staticmethod
    def parse_date(date_str: str) -> Optional[datetime.date]:
        """
        Parse a date string using multiple parsing strategies.

        Args:
            date_str: The date string to parse

        Returns:
            A datetime.date object if parsing succeeds, None otherwise
        """

        if not isinstance(date_str, str):
            return None

        clean_str = date_str.strip()

        if not clean_str or len(clean_str) > MAX_INPUT_LENGTH:
            return None

        if unix_date := DateParser._parse_unix_timestamp(clean_str):
            return DateParser._validate_date_bounds(unix_date)

        clean_str = DAY_NAME_REGEX.sub("", clean_str)
        clean_str = clean_str.replace("T", " ")

        if relative_date := DateParser._get_relative_date(clean_str.lower()):
            return DateParser._validate_date_bounds(relative_date)

        if julian_date := DateParser._parse_julian(clean_str):
            return DateParser._validate_date_bounds(julian_date)

        if excel_date := DateParser._parse_excel_serial(clean_str):
            return DateParser._validate_date_bounds(excel_date)

        if fiscal_date := DateParser._parse_fiscal_quarter(clean_str):
            return DateParser._validate_date_bounds(fiscal_date)

        if special_format_date := DateParser._parse_special_formats(clean_str):
            return DateParser._validate_date_bounds(special_format_date)

        if COMPACT_DATE_REGEX.match(clean_str):
            if numeric_date := DateParser._parse_compact_numeric(clean_str):
                return DateParser._validate_date_bounds(numeric_date)

        normalized_case = clean_str.title()
        for fmt in DateParser.DATE_FORMATS:
            if parsed_date := DateParser._try_strptime(normalized_case, fmt):
                has_day = any(marker in fmt.lower() for marker in ["%d", "%j", "%u"])
                if not has_day:
                    result = parsed_date.replace(day=1).date()
                else:
                    result = parsed_date.date()
                return DateParser._validate_date_bounds(result)

        return None

    @staticmethod
    def _validate_date_bounds(date: Optional[datetime.date]) -> Optional[datetime.date]:
        """
        Validate that a parsed date is within reasonable year bounds.

        Args:
            date: The date to validate

        Returns:
            The date if valid, None if out of bounds
        """
        if date is None:
            return None

        if not (MIN_VALID_YEAR <= date.year <= MAX_VALID_YEAR):
            return None

        return date

    @staticmethod
    def _get_relative_date(date_str: str) -> Optional[datetime.date]:
        """
        Parse relative date strings like 'today', 'yesterday', 'tomorrow', etc.

        Args:
            date_str: The relative date string to parse

        Returns:
            A datetime.date object if recognized, None otherwise
        """
        today = datetime.date.today()
        relative_dates = {
            "today": today,
            "yesterday": today - datetime.timedelta(days=1),
            "tomorrow": today + datetime.timedelta(days=1),
            "last week": today - datetime.timedelta(weeks=1),
            "next week": today + datetime.timedelta(weeks=1),
            "last month": today - datetime.timedelta(days=30),
            "next month": today + datetime.timedelta(days=30),
            "last year": today - datetime.timedelta(days=365),
            "next year": today + datetime.timedelta(days=365),
            "now": today,
        }
        return relative_dates.get(date_str)

    @staticmethod
    def _try_strptime(date_str: str, fmt: str) -> Optional[datetime.datetime]:
        try:
            return datetime.datetime.strptime(date_str, fmt)
        except ValueError:
            return None

    @staticmethod
    def _parse_special_formats(date_str: str) -> Optional[datetime.date]:
        """
        Parse 'day of month' and ordinal formats (e.g., "25th of December 1990").

        Args:
            date_str: The date string to parse

        Returns:
            A datetime.date object if parsing succeeds, None otherwise
        """
        if match := DAY_OF_MONTH_REGEX.match(date_str):
            day, month, year = match.groups()
            clean_str = f"{day} {month} {year}"
            for fmt in DateParser.NATURAL_FORMATS:
                if parsed := DateParser._try_strptime(clean_str, fmt):
                    return parsed.date()

        if ORDINAL_SUFFIX_REGEX.search(date_str):
            clean_str = ORDINAL_SUFFIX_REGEX.sub(r"\1", date_str)
            for fmt in DateParser.NATURAL_FORMATS:
                if parsed := DateParser._try_strptime(clean_str, fmt):
                    return parsed.date()

        return None

    @staticmethod
    def _parse_compact_numeric(date_str: str) -> Optional[datetime.date]:
        """
        Parse compact numeric date formats like YYYYMMDD, DDMMYY, etc.

        Args:
            date_str: The compact numeric date string

        Returns:
            A datetime.date object if parsing succeeds, None otherwise
        """
        parsers = {
            8: [
                lambda s: (s[0:4], s[4:6], s[6:8]),
                lambda s: (s[4:8], s[2:4], s[0:2]),
                lambda s: (s[4:8], s[0:2], s[2:4]),
            ],
            6: [
                lambda s: (s[4:6], s[0:2], s[2:4]),
                lambda s: (s[4:6], s[2:4], s[0:2]),
                lambda s: (s[0:2], s[2:4], s[4:6]),
            ],
        }

        if len(date_str) in parsers:
            for parser in parsers[len(date_str)]:
                y, m, d = parser(date_str)
                if len(y) == 2:
                    date = DateParser._try_create_date_from_2_digit_year(y, m, d)
                    if date:
                        return date
                else:
                    date = DateParser._try_create_date(y, m, d)
                    if date:
                        return date
        return None

    @staticmethod
    def _parse_julian(date_str: str) -> Optional[datetime.date]:
        """
        Parse Julian date format YYYY-DDD where DDD is the day of year.

        Args:
            date_str: The Julian date string to parse

        Returns:
            A datetime.date object if parsing succeeds, None otherwise
        """
        if match := JULIAN_DATE_REGEX.match(date_str):
            year, day_of_year = map(int, match.groups())
            max_days = 366 if isleap(year) else 365
            if not 1 <= day_of_year <= max_days:
                return None
            try:
                return datetime.date(year, 1, 1) + datetime.timedelta(days=day_of_year - 1)
            except (ValueError, OverflowError):
                return None
        return None

    @staticmethod
    def _parse_unix_timestamp(date_str: str) -> Optional[datetime.date]:
        """
        Parse Unix timestamp (seconds since epoch, Jan 1, 1970).

        Args:
            date_str: The Unix timestamp string to parse

        Returns:
            A datetime.date object if parsing succeeds, None otherwise
        """
        if match := UNIX_TIMESTAMP_REGEX.match(date_str):
            try:
                timestamp = int(match.group(1))
                if 0 <= timestamp <= 4102444800:
                    dt = datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc)
                    return dt.date()
            except (ValueError, OSError, OverflowError):
                return None
        return None

    @staticmethod
    def _parse_excel_serial(date_str: str) -> Optional[datetime.date]:
        """
        Parse Excel serial date number (days since Jan 1, 1900).

        Args:
            date_str: The Excel serial number string

        Returns:
            A datetime.date object if parsing succeeds, None otherwise

        Note:
            Excel incorrectly treats 1900 as a leap year, which is handled in this implementation.
        """
        if not EXCEL_SERIAL_REGEX.match(date_str) or len(date_str) == 6:
            return None

        try:
            serial = int(date_str)

            if len(date_str) == 4 and MIN_VALID_YEAR <= serial <= MAX_VALID_YEAR:
                return None

            if not (1 <= serial <= 2958465):
                return None

            excel_epoch = datetime.date(1899, 12, 31)

            if serial >= 60:
                result_date = excel_epoch + datetime.timedelta(days=serial - 1)
            else:
                result_date = excel_epoch + datetime.timedelta(days=serial)

            return result_date
        except (ValueError, OverflowError):
            return None

    @staticmethod
    def _parse_fiscal_quarter(date_str: str) -> Optional[datetime.date]:
        """
        Parse fiscal quarter format like '2023-Q4' or '2023 Q4'.

        Args:
            date_str: The fiscal quarter string to parse

        Returns:
            The first day of the quarter as a datetime.date object, None if parsing fails

        Note:
            Assumes calendar year quarters: Q1=Jan 1, Q2=Apr 1, Q3=Jul 1, Q4=Oct 1
        """
        if match := FISCAL_QUARTER_REGEX.match(date_str):
            try:
                year = int(match.group(1))
                quarter = int(match.group(2))

                quarter_start_month = {1: 1, 2: 4, 3: 7, 4: 10}
                month = quarter_start_month[quarter]

                return datetime.date(year, month, 1)
            except (ValueError, KeyError):
                return None
        return None

    @staticmethod
    def _try_create_date(y: str, m: str, d: str) -> Optional[datetime.date]:
        """
        Create a date from year, month, and day strings.

        Args:
            y: Year string
            m: Month string
            d: Day string

        Returns:
            A datetime.date object if valid, None otherwise
        """
        try:
            return datetime.date(int(y), int(m), int(d))
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _try_create_date_from_2_digit_year(y: str, m: str, d: str) -> Optional[datetime.date]:
        """
        Create a date from 2-digit year, month, and day strings.

        Args:
            y: 2-digit year string (00-49 = 2000-2049, 50-99 = 1950-1999)
            m: Month string
            d: Day string

        Returns:
            A datetime.date object if valid, None otherwise
        """
        try:
            year_int = int(y)
            full_year = 2000 + year_int if year_int < 50 else 1900 + year_int
            return datetime.date(full_year, int(m), int(d))
        except (ValueError, TypeError):
            return None


class AgeCalculator:
    """
    Handles precise age calculation and output formatting.

    Provides methods for calculating age with accurate handling of leap years,
    month-end boundaries, and leap day birthdays. All methods are static.
    """

    @staticmethod
    def calculate_age(birthday: datetime.date, today: Optional[datetime.date] = None) -> AgeResult:
        """
        Calculate precise age from a birthday to a given date.

        Args:
            birthday: The birthdate to calculate age from
            today: The reference date for calculation (defaults to today)

        Returns:
            AgeResult containing years, months, days, total days lived,
            day of week born, and countdown to next birthday

        Raises:
            ValueError: If birthday is in the future relative to today

        Note:
            Handles leap day birthdays (Feb 29) correctly and accounts for varying month lengths.
        """
        today = today or datetime.date.today()
        if birthday > today:
            raise ValueError("Birthday cannot be in the future.")

        years = (
            today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))
        )

        months = today.month - birthday.month
        if today.day < birthday.day:
            months -= 1
        if months < 0:
            months += 12

        if today.day >= birthday.day:
            days = today.day - birthday.day
        else:
            first_day_of_current_month = today.replace(day=1)
            last_day_of_prev_month = first_day_of_current_month - datetime.timedelta(days=1)
            effective_day = min(birthday.day, last_day_of_prev_month.day)
            anniversary_in_prev_month = last_day_of_prev_month.replace(day=effective_day)
            days = (today - anniversary_in_prev_month).days

        total_days = (today - birthday).days

        try:
            next_birthday = birthday.replace(year=today.year)
        except ValueError:
            next_birthday = birthday.replace(year=today.year, day=28)

        if next_birthday < today:
            try:
                next_birthday = birthday.replace(year=today.year + 1)
            except ValueError:
                next_birthday = birthday.replace(year=today.year + 1, day=28)

        next_birthday_in_days = (next_birthday - today).days

        return AgeResult(
            years=years,
            months=months,
            days=days,
            total_days=total_days,
            birth_day_of_week=birthday.strftime("%A"),
            next_birthday_in_days=next_birthday_in_days,
        )

    @staticmethod
    def format_age_output(birthday: datetime.date, age_data: AgeResult) -> str:
        """
        Format age calculation results as a human-readable string.

        Args:
            birthday: The birthdate
            age_data: The AgeResult object containing age information

        Returns:
            A formatted string with age details and next birthday information
        """
        age_parts = []
        if age_data.years > 0:
            plural = "s" if age_data.years != 1 else ""
            age_parts.append(f"{age_data.years} year{plural}")
        if age_data.months > 0:
            plural = "s" if age_data.months != 1 else ""
            age_parts.append(f"{age_data.months} month{plural}")
        if age_data.days > 0 or not age_parts:
            plural = "s" if age_data.days != 1 else ""
            age_parts.append(f"{age_data.days} day{plural}")

        if len(age_parts) > 1:
            age_str = ", ".join(age_parts[:-1]) + f" and {age_parts[-1]}"
        else:
            age_str = age_parts[0] if age_parts else "0 days"

        if age_data.next_birthday_in_days == 0:
            birthday_msg = "Happy Birthday!"
        else:
            plural = "day" if age_data.next_birthday_in_days == 1 else "days"
            birthday_msg = f"Your next birthday is in {age_data.next_birthday_in_days} {plural}!"

        return (
            f"\nResults:\n--------------------\n"
            f"Born on a {age_data.birth_day_of_week}: {birthday.strftime('%B %d, %Y')}\n"
            f"You are {age_str} old.\n"
            f"That's a total of {age_data.total_days:,} days!\n\n"
            f"{birthday_msg}\n"
        )


class AgeCalculatorApp:
    """Main application class for handling interactive user input and output."""

    EXIT_COMMANDS = {"quit", "exit", "q"}

    def __init__(self, date_parser: DateParser, age_calculator: AgeCalculator):
        self.date_parser = date_parser
        self.age_calculator = age_calculator

    def run(self) -> None:
        """
        Start the main interactive application loop.

        Prompts for user input, parses dates, calculates age, and displays results.
        Continues until user enters an exit command.
        """
        self._display_welcome()

        while True:
            try:
                user_input = self._get_user_input()
                if user_input.lower() in self.EXIT_COMMANDS:
                    print("Goodbye!")
                    break

                if not user_input:
                    print("Warning: Please enter a birthday.")
                    continue

                birthday = self.date_parser.parse_date(user_input)
                if not birthday:
                    message = "Sorry, that date format was not recognized. Please try again."
                    print(f"Error: {message}")
                    continue

                age_data = self.age_calculator.calculate_age(birthday)
                output = self.age_calculator.format_age_output(birthday, age_data)
                print(output)
            except ValueError as e:
                print(f"Error: {str(e)}")
            except (KeyboardInterrupt, EOFError):
                print(f"\n\nGoodbye!")
                break

    def _display_welcome(self) -> None:
        """Display a welcome message with usage instructions and supported date formats."""
        welcome_text = """
Age Calculator
==============================
Find out your age down to the day, discover the
day of the week you were born, and see how long
until your next birthday!

Supports 100+ date formats! Try any of these:
 - 25 Dec 1990 (natural language)
 - 12/25/1990 (US format)
 - 25.12.1990 (European format)
 - 19901225 (compact numeric)
 - 659318400 (Unix timestamp)
 - today, yesterday, last year (relative)
 - 1990 (year only)

Type 'quit' or 'exit' to close the program.
==============================
"""
        print(welcome_text)

    def _get_user_input(self) -> str:
        """
        Prompt the user for their birthday input.

        Returns:
            The user's input string, stripped of whitespace
        """
        return input("Enter your birthday: ").strip()


def main() -> None:
    """
    Entry point for the age calculator application.

    Supports both direct mode (with command-line argument) and interactive mode.
    If a birthday argument is provided, calculates and displays age immediately.
    Otherwise, starts interactive mode for multiple calculations.
    """
    parser = argparse.ArgumentParser(
        description="A robust CLI tool to calculate age from a birthday.",
        epilog="If no birthday is provided, the application will start in interactive mode.",
    )
    parser.add_argument(
        "birthday",
        nargs="?",
        default=None,
        help="The birthday string to parse (e.g., 'Dec 25 1990').",
    )
    args = parser.parse_args()

    date_parser = DateParser()
    age_calculator = AgeCalculator()

    if args.birthday:
        try:
            birthday_date = date_parser.parse_date(args.birthday)
            if not birthday_date:
                error_msg = f"The date format was not recognized: '{args.birthday}'"
                print(f"Error: {error_msg}")
                return

            age_data = age_calculator.calculate_age(birthday_date)
            output = age_calculator.format_age_output(birthday_date, age_data)
            print(output)
        except ValueError as e:
            print(f"Error: {str(e)}")
        except (KeyboardInterrupt, EOFError):
            print(f"\n\nGoodbye!")
    else:
        app = AgeCalculatorApp(date_parser, age_calculator)
        app.run()


if __name__ == "__main__":
    main()
