#!/usr/bin/env python3

"""
Age Calculator - A comprehensive tool for calculating ages from various date formats.

Author: Age Calculator Project
Version: 5.0.2
"""

import argparse
import datetime
import re
from calendar import isleap
from dataclasses import dataclass
from typing import List, Optional

DAY_NAME_REGEX = re.compile(
    r"^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|Mon|Tue|Wed|Thu|Fri|Sat|Sun),?\s*",
    re.IGNORECASE
)
ORDINAL_SUFFIX_REGEX = re.compile(r"(\d{1,2})(st|nd|rd|th)", re.IGNORECASE)
DAY_OF_MONTH_REGEX = re.compile(r"(\d{1,2})\s+of\s+([a-zA-Z]+)\s+(\d{4})", re.IGNORECASE)
COMPACT_DATE_REGEX = re.compile(r"^\d{6,8}$")
JULIAN_DATE_REGEX = re.compile(r"^(\d{4})-(\d{1,3})$")
UNIX_TIMESTAMP_REGEX = re.compile(r"^(0|\d{9,10})$")

@dataclass
class AgeResult:
    """A structured container for age calculation results."""
    years: int
    months: int
    days: int
    total_days: int
    birth_day_of_week: str
    next_birthday_in_days: int



class DateParser:
    """Handles parsing of various date formats without external dependencies."""

    DATE_FORMATS: List[str] = [
        "%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d", "%Y %m %d",
        "%m/%d/%Y", "%m-%d-%Y", "%m.%d.%Y", "%m %d %Y",
        "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y", "%d %m %Y",
        "%B %d, %Y", "%b %d, %Y", "%d %B, %Y", "%d %b, %Y",
        "%B %d %Y", "%b %d %Y", "%d %B %Y", "%d %b %Y",
        "%d-%B-%Y", "%d-%b-%Y", "%B-%d-%Y", "%b-%d-%Y",
        "%Y %B %d", "%Y %b %d", "%Y, %B %d", "%Y, %b %d",
        "%m/%d/%y", "%m-%d-%y", "%m.%d.%y", "%d/%m/%y",
        "%d-%m/%y", "%d.%m.%y", "%y/%m/%d", "%y-%m-%d",
        "%y.%m.%d", "%m %d %y", "%d %m %y", "%y %m %d",
        "%G-W%V-%u",
        "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M", "%Y/%m/%d %H:%M:%S",
        "%m/%d/%Y %I:%M:%S %p", "%m/%d/%Y %I:%M %p",
        "%d-%m-%Y %H:%M:%S", "%d-%m-%Y %H:%M",
        "%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M",
        "%a, %d %b %Y %H:%M:%S",
        "%a %b %d %H:%M:%S %Y",
        "%a %d %b %Y",
        "%B %Y", "%b %Y", "%Y-%m", "%m/%Y",
        "%m-%Y", "%m.%Y", "%Y %B", "%Y %b",
        "%d.%m.%y", "%d.%m.%Y",
        "%d%b%Y", "%Y%b%d", "%d-%b-%Y", "%d %b %Y",
        "%Y",
    ]

    NATURAL_FORMATS: List[str] = [
        "%B %d, %Y", "%b %d, %Y", "%d %B, %Y", "%d %b, %Y",
        "%B %d %Y", "%b %d %Y", "%d %B %Y", "%d %b %Y",
    ]

    @staticmethod
    def parse_date(date_str: str) -> Optional[datetime.date]:
        """Parse a date string by attempting a cascade of parsing strategies."""
        clean_str = date_str.strip()
        if not clean_str:
            return None

        if unix_date := DateParser._parse_unix_timestamp(clean_str):
            return unix_date

        clean_str = DAY_NAME_REGEX.sub("", clean_str)
        clean_str = clean_str.replace('T', ' ')

        if relative_date := DateParser._get_relative_date(clean_str.lower()):
            return relative_date
        if julian_date := DateParser._parse_julian(clean_str):
            return julian_date
        if special_format_date := DateParser._parse_special_formats(clean_str):
            return special_format_date
        if COMPACT_DATE_REGEX.match(clean_str):
            if numeric_date := DateParser._parse_compact_numeric(clean_str):
                return numeric_date

        for fmt in DateParser.DATE_FORMATS:
            if parsed_date := DateParser._try_strptime(clean_str.title(), fmt):
                has_day = any(marker in fmt.lower() for marker in ["%d", "%j", "%u"])
                if not has_day:
                    return parsed_date.replace(day=1).date()
                return parsed_date.date()

        return None

    @staticmethod
    def _get_relative_date(date_str: str) -> Optional[datetime.date]:
        """Parse relative date strings like 'today', 'yesterday', 'tomorrow', etc."""
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
        Handles 'day of month' and ordinal formats by cleaning them and
        attempting a direct parse with common natural language formats.
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
        """Parse compact numeric formats like YYYYMMDD, DDMMYY, etc."""
        parsers = {
            8: [
                lambda s: (s[0:4], s[4:6], s[6:8]),  # YYYYMMDD
                lambda s: (s[4:8], s[2:4], s[0:2]),  # DDMMYYYY
                lambda s: (s[4:8], s[0:2], s[2:4]),  # MMDDYYYY
            ],
            6: [
                lambda s: (s[4:6], s[0:2], s[2:4]),  # DDMMYY
                lambda s: (s[4:6], s[2:4], s[0:2]),  # MMDDYY
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
        """Parse Julian date format YYYY-DDD."""
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
        """Parse Unix timestamp (seconds since epoch)."""
        if match := UNIX_TIMESTAMP_REGEX.match(date_str):
            try:
                timestamp = int(match.group(1))
                if 0 <= timestamp <= 4102444800:
                    dt = datetime.datetime.fromtimestamp(timestamp)
                    return dt.date()
            except (ValueError, OSError, OverflowError):
                return None
        return None

    @staticmethod
    def _try_create_date(y: str, m: str, d: str) -> Optional[datetime.date]:
        """Create a date from year, month, day strings."""
        try:
            return datetime.date(int(y), int(m), int(d))
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _try_create_date_from_2_digit_year(y: str, m: str, d: str) -> Optional[datetime.date]:
        """Create a date from 2-digit year and month, day strings."""
        try:
            year_int = int(y)
            full_year = 2000 + year_int if year_int < 50 else 1900 + year_int
            return datetime.date(full_year, int(m), int(d))
        except (ValueError, TypeError):
            return None

class AgeCalculator:
    """Handles age calculation and formatting."""

    @staticmethod
    def calculate_age(birthday: datetime.date, today: Optional[datetime.date] = None) -> AgeResult:
        """Calculates the precise age and information about the next birthday."""
        today = today or datetime.date.today()
        if birthday > today:
            raise ValueError("Birthday cannot be in the future.")

        years = today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))

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
            years=years, months=months, days=days, total_days=total_days,
            birth_day_of_week=birthday.strftime('%A'),
            next_birthday_in_days=next_birthday_in_days
        )
    
    @staticmethod
    def format_age_output(
        birthday: datetime.date,
        age_data: AgeResult
    ) -> str:
        """Format age calculation results as a human-readable string."""
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

        birthday_msg = "Happy Birthday!" if age_data.next_birthday_in_days == 0 else f"Your next birthday is in {age_data.next_birthday_in_days} days!"

        return (
            f"\nResults:\n--------------------\n"
            f"Born on a {age_data.birth_day_of_week}: {birthday.strftime('%B %d, %Y')}\n"
            f"You are {age_str} old.\n"
            f"That's a total of {age_data.total_days:,} days!\n\n"
            f"{birthday_msg}\n"
        )

class AgeCalculatorApp:
    """Main application class for handling user interaction."""
    EXIT_COMMANDS = {"quit", "exit", "q"}

    def __init__(
        self,
        date_parser: DateParser,
        age_calculator: AgeCalculator
    ):
        self.date_parser = date_parser
        self.age_calculator = age_calculator

    def run(self) -> None:
        """Starts the main application loop."""
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
        """Prints a visually appealing and informative welcome message."""
        welcome_text = """
Age Calculator
==============================
Find out your age down to the day, discover the
day of the week you were born, and see how long
until your next birthday!

Supports 70+ date formats! Try any of these:
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
        """Prompts the user for their birthday."""
        return input("Enter your birthday: ").strip()

def main() -> None:
    """
    Entry point for the age calculator application.
    Supports both direct (command-line argument) and interactive modes.
    """
    parser = argparse.ArgumentParser(
        description="A robust CLI tool to calculate age from a birthday.",
        epilog="If no birthday is provided, the application will start in interactive mode."
    )
    parser.add_argument(
        "birthday",
        nargs="?",
        default=None,
        help="The birthday string to parse (e.g., 'Dec 25 1990')."
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
