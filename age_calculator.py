#!/usr/bin/env python3

"""
Age Calculator - A tool for calculating ages from various date formats.

Supports 100+ international date formats, accurate age calculation with leap
year handling, and both CLI and programmatic interfaces. Includes input
validation and bounds checking for security.
"""

import argparse
import datetime
import re
from calendar import isleap
from dataclasses import dataclass
from typing import Callable, Optional

__all__ = ["AgeCalculator", "AgeCalculatorApp", "AgeResult", "DateParser", "main"]

# Constants - Validation Limits
MAX_INPUT_LENGTH = 1000
MIN_VALID_YEAR = 1900
MAX_VALID_YEAR = 2100
MAX_UNIX_TIMESTAMP = 4102444800
MAX_EXCEL_SERIAL = 2958465

# Constants - Compiled Regular Expressions
COMPACT_DATE_REGEX = re.compile(r"^\d{6,8}$")
DAY_NAME_REGEX = re.compile(
    r"^(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|"
    r"Mon|Tue|Wed|Thu|Fri|Sat|Sun),?\s*",
    re.IGNORECASE,
)
DAY_OF_MONTH_REGEX = re.compile(
    r"(\d{1,2})(?:st|nd|rd|th)?\s+of\s+([a-z]+)\s+(\d{4})",
    re.IGNORECASE,
)
EXCEL_SERIAL_REGEX = re.compile(r"^\d{1,5}$|^\d{7}$")
FISCAL_QUARTER_REGEX = re.compile(r"^(\d{4})[-\s]?Q([1-4])$", re.IGNORECASE)
JULIAN_DATE_REGEX = re.compile(r"^(\d{4})-(\d{1,3})$")
ORDINAL_SUFFIX_REGEX = re.compile(r"(\d{1,2})(?:st|nd|rd|th)", re.IGNORECASE)
UNIX_TIMESTAMP_REGEX = re.compile(r"^0$|^[1-9]\d{8,9}$")


@dataclass(frozen=True, slots=True)
class AgeResult:
    """Container for age calculation results."""

    years: int
    months: int
    days: int
    total_days: int
    birth_day_of_week: str
    next_birthday_in_days: int


class DateParser:
    """Parses dates from various formats including ISO, natural language, and specialized formats."""

    DATE_FORMATS: tuple[str, ...] = (
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
    )

    NATURAL_FORMATS: tuple[str, ...] = (
        "%B %d, %Y",
        "%b %d, %Y",
        "%d %B, %Y",
        "%d %b, %Y",
        "%B %d %Y",
        "%b %d %Y",
        "%d %B %Y",
        "%d %b %Y",
    )

    _FORMATS_WITH_DAY: frozenset[str] = frozenset(
        fmt
        for fmt in DATE_FORMATS
        if any(marker in fmt.lower() for marker in ("%d", "%j", "%u"))
    )

    _RELATIVE_DATE_OFFSETS: dict[str, int] = {
        "now": 0,
        "today": 0,
        "tomorrow": 1,
        "yesterday": -1,
    }

    _RELATIVE_DATE_TIMEDELTAS: dict[str, datetime.timedelta] = {
        "last month": datetime.timedelta(days=-30),
        "last week": datetime.timedelta(weeks=-1),
        "last year": datetime.timedelta(days=-365),
        "next month": datetime.timedelta(days=30),
        "next week": datetime.timedelta(weeks=1),
        "next year": datetime.timedelta(days=365),
    }

    @classmethod
    def parse_date(cls, date_str: str) -> Optional[datetime.date]:
        """
        Parse a date string using multiple parsing strategies.

        Args:
            date_str: The date string to parse.

        Returns:
            A datetime.date object if parsing succeeds, None otherwise.
        """
        if not isinstance(date_str, str):
            return None

        clean_str = date_str.strip()

        if not clean_str or len(clean_str) > MAX_INPUT_LENGTH:
            return None

        if unix_date := cls._parse_unix_timestamp(clean_str):
            return cls._validate_date_bounds(unix_date)

        clean_str = DAY_NAME_REGEX.sub("", clean_str)
        clean_str = clean_str.replace("T", " ")

        if parsed := cls._try_specialized_parsers(clean_str):
            return cls._validate_date_bounds(parsed)

        return cls._try_standard_formats(clean_str)

    @classmethod
    def _try_specialized_parsers(cls, clean_str: str) -> Optional[datetime.date]:
        """Try all specialized date parsers in sequence."""
        lower_str = clean_str.lower()

        if lower_str in cls._RELATIVE_DATE_OFFSETS:
            return datetime.date.today() + datetime.timedelta(
                days=cls._RELATIVE_DATE_OFFSETS[lower_str]
            )

        if lower_str in cls._RELATIVE_DATE_TIMEDELTAS:
            return datetime.date.today() + cls._RELATIVE_DATE_TIMEDELTAS[lower_str]

        parsers: tuple[Callable[[str], Optional[datetime.date]], ...] = (
            cls._parse_julian,
            cls._parse_excel_serial,
            cls._parse_fiscal_quarter,
            cls._parse_special_formats,
        )

        for parser in parsers:
            if result := parser(clean_str):
                return result

        if COMPACT_DATE_REGEX.match(clean_str):
            return cls._parse_compact_numeric(clean_str)

        return None

    @classmethod
    def _try_standard_formats(cls, clean_str: str) -> Optional[datetime.date]:
        """Try parsing with standard date format strings."""
        normalized_case = clean_str.title()

        for fmt in cls.DATE_FORMATS:
            try:
                parsed_date = datetime.datetime.strptime(normalized_case, fmt)
                if fmt in cls._FORMATS_WITH_DAY:
                    result = parsed_date.date()
                else:
                    result = parsed_date.replace(day=1).date()
                return cls._validate_date_bounds(result)
            except ValueError:
                continue

        return None

    @classmethod
    def _parse_special_formats(cls, date_str: str) -> Optional[datetime.date]:
        """Parse 'day of month' and ordinal formats (e.g., '25th of December 1990')."""
        if match := DAY_OF_MONTH_REGEX.match(date_str):
            day, month, year = match.groups()
            clean_str = f"{day} {month} {year}"
            for fmt in cls.NATURAL_FORMATS:
                try:
                    return datetime.datetime.strptime(clean_str, fmt).date()
                except ValueError:
                    continue

        if ORDINAL_SUFFIX_REGEX.search(date_str):
            clean_str = ORDINAL_SUFFIX_REGEX.sub(r"\1", date_str)
            for fmt in cls.NATURAL_FORMATS:
                try:
                    return datetime.datetime.strptime(clean_str, fmt).date()
                except ValueError:
                    continue

        return None

    @staticmethod
    def _validate_date_bounds(date: Optional[datetime.date]) -> Optional[datetime.date]:
        """Validate that a parsed date is within reasonable year bounds."""
        if date is None:
            return None

        if MIN_VALID_YEAR <= date.year <= MAX_VALID_YEAR:
            return date

        return None

    @staticmethod
    def _parse_compact_numeric(date_str: str) -> Optional[datetime.date]:
        """Parse compact numeric date formats like YYYYMMDD, DDMMYY, etc."""
        length = len(date_str)

        if length == 8:
            if date := DateParser._try_create_date(
                date_str[0:4], date_str[4:6], date_str[6:8]
            ):
                return date
            if date := DateParser._try_create_date(
                date_str[4:8], date_str[2:4], date_str[0:2]
            ):
                return date
            if date := DateParser._try_create_date(
                date_str[4:8], date_str[0:2], date_str[2:4]
            ):
                return date

        elif length == 6:
            if date := DateParser._try_create_date_from_2_digit_year(
                date_str[0:2], date_str[2:4], date_str[4:6]
            ):
                return date
            if date := DateParser._try_create_date_from_2_digit_year(
                date_str[4:6], date_str[2:4], date_str[0:2]
            ):
                return date
            if date := DateParser._try_create_date_from_2_digit_year(
                date_str[4:6], date_str[0:2], date_str[2:4]
            ):
                return date

        return None

    @staticmethod
    def _parse_excel_serial(date_str: str) -> Optional[datetime.date]:
        """
        Parse Excel serial date number (days since Jan 1, 1900).

        Note:
            Excel incorrectly treats 1900 as a leap year, which is handled here.
        """
        if not EXCEL_SERIAL_REGEX.match(date_str):
            return None

        try:
            serial = int(date_str)

            if len(date_str) == 4 and MIN_VALID_YEAR <= serial <= MAX_VALID_YEAR:
                return None

            if not (1 <= serial <= MAX_EXCEL_SERIAL):
                return None

            excel_epoch = datetime.date(1899, 12, 31)

            if serial >= 60:
                return excel_epoch + datetime.timedelta(days=serial - 1)
            return excel_epoch + datetime.timedelta(days=serial)
        except (ValueError, OverflowError):
            return None

    @staticmethod
    def _parse_fiscal_quarter(date_str: str) -> Optional[datetime.date]:
        """
        Parse fiscal quarter format like '2023-Q4' or '2023 Q4'.

        Returns the first day of the quarter.
        """
        if match := FISCAL_QUARTER_REGEX.match(date_str):
            try:
                year = int(match.group(1))
                quarter = int(match.group(2))
                month = (quarter - 1) * 3 + 1
                return datetime.date(year, month, 1)
            except ValueError:
                pass
        return None

    @staticmethod
    def _parse_julian(date_str: str) -> Optional[datetime.date]:
        """Parse Julian date format YYYY-DDD where DDD is the day of year."""
        if match := JULIAN_DATE_REGEX.match(date_str):
            try:
                year = int(match.group(1))
                day_of_year = int(match.group(2))
                max_days = 366 if isleap(year) else 365

                if 1 <= day_of_year <= max_days:
                    return datetime.date(year, 1, 1) + datetime.timedelta(
                        days=day_of_year - 1
                    )
            except (ValueError, OverflowError):
                pass
        return None

    @staticmethod
    def _parse_unix_timestamp(date_str: str) -> Optional[datetime.date]:
        """Parse Unix timestamp (seconds since epoch, Jan 1, 1970)."""
        if UNIX_TIMESTAMP_REGEX.match(date_str):
            try:
                timestamp = int(date_str)
                if 0 <= timestamp <= MAX_UNIX_TIMESTAMP:
                    return datetime.datetime.fromtimestamp(
                        timestamp, datetime.timezone.utc
                    ).date()
            except (ValueError, OSError, OverflowError):
                pass
        return None

    @staticmethod
    def _try_create_date(y: str, m: str, d: str) -> Optional[datetime.date]:
        """Create a date from year, month, and day strings."""
        try:
            year, month, day = int(y), int(m), int(d)
            if 1 <= month <= 12 and 1 <= day <= 31:
                return datetime.date(year, month, day)
        except (ValueError, TypeError):
            pass
        return None

    @staticmethod
    def _try_create_date_from_2_digit_year(
        y: str, m: str, d: str
    ) -> Optional[datetime.date]:
        """
        Create a date from 2-digit year, month, and day strings.

        Uses pivot year: 00-49 = 2000-2049, 50-99 = 1950-1999.
        """
        try:
            year_int = int(y)
            month, day = int(m), int(d)

            if not (1 <= month <= 12 and 1 <= day <= 31):
                return None

            full_year = 2000 + year_int if year_int < 50 else 1900 + year_int
            return datetime.date(full_year, month, day)
        except (ValueError, TypeError):
            return None


class AgeCalculator:
    """
    Handles precise age calculation and output formatting.

    Provides methods for calculating age with accurate handling of leap years,
    month-end boundaries, and leap day birthdays.
    """

    _DAYS_OF_WEEK: tuple[str, ...] = (
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    )

    @classmethod
    def calculate_age(
        cls, birthday: datetime.date, today: Optional[datetime.date] = None
    ) -> AgeResult:
        """
        Calculate precise age from a birthday to a given date.

        Args:
            birthday: The birthdate to calculate age from.
            today: The reference date for calculation (defaults to today).

        Returns:
            AgeResult containing years, months, days, total days lived,
            day of week born, and countdown to next birthday.

        Raises:
            ValueError: If birthday is in the future relative to today.
        """
        if today is None:
            today = datetime.date.today()

        if birthday > today:
            raise ValueError("Birthday cannot be in the future.")

        had_birthday_this_year = (today.month, today.day) >= (
            birthday.month,
            birthday.day,
        )
        years = today.year - birthday.year - (0 if had_birthday_this_year else 1)

        months = today.month - birthday.month
        if today.day < birthday.day:
            months -= 1
        if months < 0:
            months += 12

        if today.day >= birthday.day:
            days = today.day - birthday.day
        else:
            first_of_month = today.replace(day=1)
            last_of_prev_month = first_of_month - datetime.timedelta(days=1)
            effective_day = min(birthday.day, last_of_prev_month.day)
            anniversary = last_of_prev_month.replace(day=effective_day)
            days = (today - anniversary).days

        total_days = (today - birthday).days
        next_birthday_in_days = cls._days_until_next_birthday(birthday, today)
        birth_day_of_week = cls._DAYS_OF_WEEK[birthday.weekday()]

        return AgeResult(
            years=years,
            months=months,
            days=days,
            total_days=total_days,
            birth_day_of_week=birth_day_of_week,
            next_birthday_in_days=next_birthday_in_days,
        )

    @classmethod
    def format_age_output(cls, birthday: datetime.date, age_data: AgeResult) -> str:
        """Format age calculation results as a human-readable string."""
        age_str = cls._format_age_string(age_data)
        birthday_msg = cls._format_birthday_message(age_data.next_birthday_in_days)

        return (
            f"\nResults:\n--------------------\n"
            f"Born on a {age_data.birth_day_of_week}: {birthday.strftime('%B %d, %Y')}\n"
            f"You are {age_str} old.\n"
            f"That's a total of {age_data.total_days:,} days!\n\n"
            f"{birthday_msg}\n"
        )

    @staticmethod
    def _days_until_next_birthday(birthday: datetime.date, today: datetime.date) -> int:
        """Calculate days until the next birthday."""
        try:
            next_birthday = birthday.replace(year=today.year)
        except ValueError:
            next_birthday = datetime.date(today.year, 2, 28)

        if next_birthday < today:
            try:
                next_birthday = birthday.replace(year=today.year + 1)
            except ValueError:
                next_birthday = datetime.date(today.year + 1, 2, 28)

        return (next_birthday - today).days

    @staticmethod
    def _format_age_string(age_data: AgeResult) -> str:
        """Format the age components into a human-readable string."""
        parts: list[str] = []

        if age_data.years > 0:
            parts.append(f"{age_data.years} year{'s' if age_data.years != 1 else ''}")

        if age_data.months > 0:
            parts.append(
                f"{age_data.months} month{'s' if age_data.months != 1 else ''}"
            )

        if age_data.days > 0 or not parts:
            parts.append(f"{age_data.days} day{'s' if age_data.days != 1 else ''}")

        if len(parts) > 1:
            return ", ".join(parts[:-1]) + f" and {parts[-1]}"
        return parts[0] if parts else "0 days"

    @staticmethod
    def _format_birthday_message(days_until_birthday: int) -> str:
        """Format the birthday countdown message."""
        if days_until_birthday == 0:
            return "Happy Birthday!"
        plural = "day" if days_until_birthday == 1 else "days"
        return f"Your next birthday is in {days_until_birthday} {plural}!"


class AgeCalculatorApp:
    """Main application class for handling interactive user input and output."""

    EXIT_COMMANDS: frozenset[str] = frozenset({"exit", "q", "quit"})

    WELCOME_TEXT: str = """
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

    def __init__(
        self,
        date_parser: Optional[DateParser] = None,
        age_calculator: Optional[AgeCalculator] = None,
    ) -> None:
        self.date_parser = date_parser or DateParser()
        self.age_calculator = age_calculator or AgeCalculator()

    def run(self) -> None:
        """
        Start the main interactive application loop.

        Prompts for user input, parses dates, calculates age, and displays results.
        Continues until user enters an exit command.
        """
        print(self.WELCOME_TEXT)

        while True:
            try:
                user_input = input("Enter your birthday: ").strip()

                if user_input.lower() in self.EXIT_COMMANDS:
                    print("Goodbye!")
                    break

                if not user_input:
                    print("Warning: Please enter a birthday.")
                    continue

                birthday = self.date_parser.parse_date(user_input)
                if not birthday:
                    print(
                        "Error: Sorry, that date format was not recognized. "
                        "Please try again."
                    )
                    continue

                age_data = self.age_calculator.calculate_age(birthday)
                print(self.age_calculator.format_age_output(birthday, age_data))

            except ValueError as e:
                print(f"Error: {e}")
            except (KeyboardInterrupt, EOFError):
                print("\n\nGoodbye!")
                break


def main() -> None:
    """
    Entry point for the age calculator application.

    Supports both direct mode (with command-line argument) and interactive mode.
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
                print(f"Error: The date format was not recognized: '{args.birthday}'")
                return

            age_data = age_calculator.calculate_age(birthday_date)
            print(age_calculator.format_age_output(birthday_date, age_data))
        except ValueError as e:
            print(f"Error: {e}")
        except (KeyboardInterrupt, EOFError):
            print("\n\nGoodbye!")
    else:
        app = AgeCalculatorApp(date_parser, age_calculator)
        app.run()


if __name__ == "__main__":
    main()
