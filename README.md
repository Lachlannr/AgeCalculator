# Age Calculator CLI

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Tests](https://img.shields.io/badge/tests-30%20passing-brightgreen)

A production-ready, dependency-free command-line tool for calculating precise ages from 100+ international date formats. Built entirely with Python's standard library, this tool handles complex edge cases like leap years, month-end boundaries, and various date representations with robust input validation.

Whether you're building a user-facing application or need programmatic age calculation, this tool provides both a CLI interface and a clean Python API. It correctly handles everything from natural language dates ("December 25th, 1990") to Unix timestamps, Excel serial numbers, and international formats.

---

## Features

### Date Format Support (100+ formats)

- **Standard formats**: ISO 8601 (`YYYY-MM-DD`), US (`MM/DD/YYYY`), European (`DD.MM.YYYY`)
- **Natural language**: `December 25, 1990`, `25th of December 1990`, `Dec 25 1990`
- **Timestamps**: Unix timestamps (`659318400`), ISO 8601 with microseconds, RFC 2822
- **Specialized formats**: Julian dates (`2023-359`), Excel serials (`36526`), fiscal quarters (`2023-Q4`)
- **Relative dates**: `today`, `yesterday`, `last year`, `next month`
- **International**: CJK formats, European variations, compact numeric (`19901225`)
- **Flexible**: Year-only (`1990`), month/year combinations

### Core Capabilities

- **Precise age calculation** in years, months, and days
- **Leap year handling** including February 29th birthdays
- **Boundary condition support** for month-end dates (e.g., Jan 31 → Feb 28/29)
- **Rich metadata**: Day of week born, total days lived, countdown to next birthday
- **Dual-mode operation**: Interactive CLI or direct command-line execution
- **Security-focused**: Input validation, bounds checking (1900-2100), length limits

---

## Tech Stack

**Zero external dependencies** — built entirely with Python 3.8+ standard library:

- [`datetime`](https://docs.python.org/3/library/datetime.html) — Date/time arithmetic and parsing
- [`re`](https://docs.python.org/3/library/re.html) — Pattern matching and input preprocessing
- [`argparse`](https://docs.python.org/3/library/argparse.html) — CLI argument handling
- [`dataclasses`](https://docs.python.org/3/library/dataclasses.html) — Structured return types
- [`calendar`](https://docs.python.org/3/library/calendar.html) — Leap year detection
- [`unittest`](https://docs.python.org/3/library/unittest.html) — Test framework

---

## Installation

**Prerequisites:** Python 3.8 or higher

```bash
# Clone the repository
git clone https://github.com/Lachlannr/AgeCalculator.git
cd AgeCalculator

# Run directly (no installation required)
python age_calculator.py

# Or make it executable
chmod +x age_calculator.py
./age_calculator.py
```

---

## Quick Start

```bash
# Calculate age from a date
python age_calculator.py "December 25, 1990"
```

**Output:**
```
Results:
--------------------
Born on a Tuesday: December 25, 1990
You are 34 years, 10 months and 20 days old.
That's a total of 12,750 days!

Your next birthday is in 51 days!
```

---

## Usage

### Command-Line Interface

**Direct mode** (single calculation):
```bash
python age_calculator.py "December 25, 1990"
```

**Interactive mode** (multiple calculations):
```bash
python age_calculator.py
# Enter dates at the prompt, type 'quit' or 'exit' to close
```

### Programmatic API

```python
from age_calculator import DateParser, AgeCalculator
import datetime

# Parse a date string
parser = DateParser()
birthday = parser.parse_date("1990-12-25")  # Returns datetime.date or None

# Calculate age
calculator = AgeCalculator()
age_result = calculator.calculate_age(birthday)

# Access results
print(f"{age_result.years} years, {age_result.months} months, {age_result.days} days")
print(f"Born on a {age_result.birth_day_of_week}")
print(f"Total days: {age_result.total_days:,}")
print(f"Next birthday in {age_result.next_birthday_in_days} days")

# Format output
formatted = calculator.format_age_output(birthday, age_result)
print(formatted)
```

### Usage Examples

```bash
# Natural language
python age_calculator.py "25th of December 1990"

# ISO format
python age_calculator.py "1990-12-25"

# Unix timestamp
python age_calculator.py "659318400"

# Relative date
python age_calculator.py "yesterday"

# Excel serial
python age_calculator.py "36526"

# Compact numeric
python age_calculator.py "19901225"
```

---

## API Documentation

### `DateParser`

Parses date strings from various formats into `datetime.date` objects.

```python
parse_date(date_str: str) -> Optional[datetime.date]
```

Parses a date string using multiple parsing strategies. Returns `None` if parsing fails.

**Parameters:**
- `date_str` (str): Date string in any supported format

**Returns:**
- `Optional[datetime.date]`: Parsed date object or `None`

**Example:**
```python
parser = DateParser()
date = parser.parse_date("Dec 25 1990")  # datetime.date(1990, 12, 25)
```

### `AgeCalculator`

Handles age calculation and output formatting.

```python
calculate_age(birthday: datetime.date, today: Optional[datetime.date] = None) -> AgeResult
```

Calculates precise age from a birthday to a reference date.

**Parameters:**
- `birthday` (datetime.date): The birthdate
- `today` (Optional[datetime.date]): Reference date (defaults to today)

**Returns:**
- `AgeResult`: Dataclass containing years, months, days, total_days, birth_day_of_week, next_birthday_in_days

**Raises:**
- `ValueError`: If birthday is in the future relative to today

**Example:**
```python
calculator = AgeCalculator()
result = calculator.calculate_age(datetime.date(1990, 12, 25))
# AgeResult(years=34, months=10, days=20, ...)
```

```python
format_age_output(birthday: datetime.date, age_data: AgeResult) -> str
```

Formats age calculation results as a human-readable string.

**Parameters:**
- `birthday` (datetime.date): The birthdate
- `age_data` (AgeResult): Age calculation result

**Returns:**
- `str`: Formatted output string

### `AgeResult`

Dataclass containing age calculation results.

**Fields:**
- `years` (int): Age in years
- `months` (int): Additional months
- `days` (int): Additional days
- `total_days` (int): Total days lived
- `birth_day_of_week` (str): Day of week born (e.g., "Monday")
- `next_birthday_in_days` (int): Days until next birthday

---

## Project Structure

```
AgeCalculator/
├── age_calculator.py      # Main application (730 lines)
├── test_age_calculator.py # Test suite (294 lines, 30 tests)
├── LICENSE                # MIT License
├── README.md              # This file
└── .gitignore             # Git ignore rules
```

### Code Organization

- **`DateParser`**: Format recognition and parsing logic
- **`AgeCalculator`**: Date arithmetic and age calculation
- **`AgeResult`**: Structured output dataclass
- **`AgeCalculatorApp`**: Interactive CLI interface

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
