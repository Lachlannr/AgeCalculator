#!/usr/bin/env python3

"""
Age Calculator - A comprehensive tool for calculating ages from various date formats.

Author: Age Calculator Project
Version: 3.0.1
"""

import datetime
import re
from typing import Dict, Optional, List

class DateParser:
    """Handles parsing of various date formats without external dependencies."""

    ORDINAL_SUFFIX_REGEX = re.compile(r"(\d)(st|nd|rd|th)", re.IGNORECASE)

    COMMON_FORMATS: List[str] = [
        "%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d",  # ISO-like
        "%m/%d/%Y", "%m-%d-%Y", "%m.%d.%Y",  # American
        "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y",  # European
    ]
    NATURAL_LANGUAGE_FORMATS: List[str] = [
        "%B %d, %Y", "%b %d, %Y", "%d %B %Y", "%d %b %Y",
    ]
    LESS_COMMON_FORMATS: List[str] = [
        "%m/%d/%y", "%m-%d-%y", "%d/%m/%y", "%d-%m-%y",  # Short year
    ]
    MONTH_ONLY_FORMATS: List[str] = ["%B %Y", "%b %Y", "%m/%Y", "%m-%Y"]

    @staticmethod
    def parse_date(date_str: str) -> Optional[datetime.date]:
        """
        Parse a date string by attempting various common formats.

        The method follows a logical cascade:
        1. Checks for relative dates ('today', 'yesterday').
        2. Tries standard numeric formats (YYYY-MM-DD, MM/DD/YYYY, etc.).
        3. Tries natural language formats ('December 25, 1990').
        4. Tries formats with ordinal day indicators ('25th Dec 1990').
        5. Tries formats with two-digit years ('12/25/90').
        6. Tries compact numeric formats ('19901225').
        7. Tries month-and-year-only formats ('Dec 1990').
        """
        date_str_strip = date_str.strip()
        date_str_lower = date_str_strip.lower()

        if relative_date := DateParser._get_relative_date(date_str_lower):
            return relative_date

        date_str_title = date_str_strip.title()

        for fmt in DateParser.COMMON_FORMATS:
            if parsed_date := DateParser._try_strptime(date_str_strip, fmt):
                return parsed_date.date()

        for fmt in DateParser.NATURAL_LANGUAGE_FORMATS:
            if parsed_date := DateParser._try_strptime(date_str_title, fmt):
                return parsed_date.date()

        if ordinal_date := DateParser._parse_ordinal(date_str_title):
            return ordinal_date

        for fmt in DateParser.LESS_COMMON_FORMATS:
            if parsed_date := DateParser._try_strptime(date_str_strip, fmt):
                return DateParser._handle_two_digit_year(parsed_date).date()

        if date_str_strip.isdigit():
            if numeric_date := DateParser._parse_compact_numeric(date_str_strip):
                return numeric_date

        for fmt in DateParser.MONTH_ONLY_FORMATS:
            if parsed_date := DateParser._try_strptime(date_str_title, fmt):
                return parsed_date.replace(day=1).date()

        return None

    @staticmethod
    def _get_relative_date(date_str: str) -> Optional[datetime.date]:
        """Parses relative date strings like 'today', 'yesterday', 'tomorrow'."""
        today = datetime.date.today()
        relative_dates = {
            "today": today,
            "yesterday": today - datetime.timedelta(days=1),
            "tomorrow": today + datetime.timedelta(days=1),
        }
        return relative_dates.get(date_str)

    @staticmethod
    def _try_strptime(date_str: str, fmt: str) -> Optional[datetime.datetime]:
        """A wrapper for strptime that returns None on failure."""
        try:
            return datetime.datetime.strptime(date_str, fmt)
        except ValueError:
            return None

    @staticmethod
    def _handle_two_digit_year(dt: datetime.datetime) -> datetime.datetime:
        """Converts a two-digit year to a four-digit year (e.g., 90 -> 1990, 05 -> 2005)."""
        if dt.year < 100:
            return dt.replace(year=dt.year + (2000 if dt.year < 50 else 1900))
        return dt

    @staticmethod
    def _parse_ordinal(date_str: str) -> Optional[datetime.date]:
        """Handles dates with ordinal indicators (e.g., '25th December 1990')."""
        if not DateParser.ORDINAL_SUFFIX_REGEX.search(date_str):
            return None
        
        clean_str = DateParser.ORDINAL_SUFFIX_REGEX.sub(r"\1", date_str)

        ordinal_parse_formats = [
            "%B %d, %Y", "%b %d, %Y",  # Month Day, Year
            "%d %B, %Y", "%d %b, %Y",  # Day Month, Year
            "%B %d %Y",  "%b %d %Y",   # Month Day Year (no comma)
            "%d %B %Y",  "%d %b %Y",   # Day Month Year (no comma)
        ]

        for fmt in ordinal_parse_formats:
            normalized_str = ' '.join(clean_str.split())
            if parsed_date := DateParser._try_strptime(normalized_str, fmt):
                return parsed_date.date()
                
        return None

    @staticmethod
    def _parse_compact_numeric(date_str: str) -> Optional[datetime.date]:
        """
        Parses compact numeric strings like YYYYMMDD, DDMMYYYY, or MMDDYY.
        NOTE: This function makes assumptions for ambiguous formats.
        The order of attempts is documented below.
        """
        if len(date_str) == 8:
            # 1. YYYYMMDD (unambiguous standard)
            if date := DateParser._try_create_date(date_str[0:4], date_str[4:6], date_str[6:8]): return date
            # 2. DDMMYYYY (common European format)
            if date := DateParser._try_create_date(date_str[4:8], date_str[2:4], date_str[0:2]): return date
            # 3. MMDDYYYY (common US format)
            if date := DateParser._try_create_date(date_str[4:8], date_str[0:2], date_str[2:4]): return date
        elif len(date_str) == 6:
            # 1. MMDDYY (common US format)
            if date := DateParser._try_create_date_from_2_digit_year(date_str[4:6], date_str[0:2], date_str[2:4]): return date
            # 2. DDMMYY (common European format)
            if date := DateParser._try_create_date_from_2_digit_year(date_str[4:6], date_str[2:4], date_str[0:2]): return date
        return None

    @staticmethod
    def _try_create_date(y: str, m: str, d: str) -> Optional[datetime.date]:
        """Attempts to create a date object from year, month, day strings."""
        try:
            return datetime.date(int(y), int(m), int(d))
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _try_create_date_from_2_digit_year(y: str, m: str, d: str) -> Optional[datetime.date]:
        """Creates a date object from strings, handling a two-digit year."""
        try:
            year_int = int(y)
            full_year = 2000 + year_int if year_int < 50 else 1900 + year_int
            return datetime.date(full_year, int(m), int(d))
        except (ValueError, TypeError):
            return None

class AgeCalculator:
    """Handles age calculation and formatting."""

    @staticmethod
    def calculate_age(birthday: datetime.date, today: Optional[datetime.date] = None) -> Dict[str, int]:
        """
        Calculates the precise age in years, months, and days.
        This method correctly handles leap years and varying month lengths.
        """
        if today is None:
            today = datetime.date.today()
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
            prev_month_last_day = today.replace(day=1) - datetime.timedelta(days=1)

            anniversary_day = min(birthday.day, prev_month_last_day.day)
            
            anniversary_in_prev_month = prev_month_last_day.replace(day=anniversary_day)
            days = (today - anniversary_in_prev_month).days

        total_days = (today - birthday).days

        return {"years": years, "months": months, "days": days, "total_days": total_days}

    @staticmethod
    def format_age_output(birthday: datetime.date, age_data: Dict[str, int]) -> str:
        """Formats the calculated age data into a user-friendly string."""
        years, months, days = age_data["years"], age_data["months"], age_data["days"]
        total_days = age_data["total_days"]

        age_parts = []
        if years > 0:
            age_parts.append(f"{years} year{'s' if years != 1 else ''}")
        if months > 0:
            age_parts.append(f"{months} month{'s' if months != 1 else ''}")
        if days > 0 or not age_parts:
            age_parts.append(f"{days} day{'s' if days != 1 else ''}")

        if len(age_parts) > 1:
            age_str = ", ".join(age_parts[:-1]) + f" and {age_parts[-1]}"
        else:
            age_str = age_parts[0] if age_parts else "0 days"

        return (
            f"\n🎉 Results:\n--------------------\n"
            f"Birthday: {birthday.strftime('%B %d, %Y')}\n"
            f"You are {age_str} old.\n"
            f"That's a total of {total_days:,} days!\n"
        )

class AgeCalculatorApp:
    """Main application class for handling user interaction."""
    EXIT_COMMANDS = {"quit", "exit", "q"}

    def __init__(self, date_parser: DateParser, age_calculator: AgeCalculator):
        self.date_parser = date_parser
        self.age_calculator = age_calculator

    def run(self) -> None:
        """Starts the main application loop."""
        self._display_welcome()
        while True:
            try:
                user_input = self._get_user_input()
                if user_input.lower() in self.EXIT_COMMANDS:
                    print("Goodbye! 👋")
                    break
                
                if not user_input:
                    print("⚠️ Please enter a birthday.")
                    continue

                birthday = self.date_parser.parse_date(user_input)
                if not birthday:
                    print("❌ Sorry, that date format was not recognized. Please try again.")
                    continue
                
                age_data = self.age_calculator.calculate_age(birthday)
                print(self.age_calculator.format_age_output(birthday, age_data))

            except ValueError as e:
                print(f"❌ Error: {e}\n")
            except KeyboardInterrupt:
                print("\n\nGoodbye! 👋")
                break
            except Exception as e:
                print(f"❌ An unexpected error occurred: {e}\n")

    def _display_welcome(self) -> None:
        """Prints the welcome message and instructions."""
        print("""
🎂 Age Calculator 🎂
==============================
Enter your birthday in any common format, for example:
• Standard: 12/25/1990, 25-12-1990, 1990.12.25
• Natural: December 25, 1990, 25th Dec 1990
• Compact: 19901225, 122590, 16052005
• Relative: today, yesterday
(Enter 'quit' or 'exit' to close)
""")

    def _get_user_input(self) -> str:
        """Prompts the user for their birthday."""
        return input("Enter your birthday: ").strip()

def main() -> None:
    """Entry point for the age calculator application."""
    parser = DateParser()
    calculator = AgeCalculator()
    app = AgeCalculatorApp(parser, calculator)
    app.run()

if __name__ == "__main__":
    main()
