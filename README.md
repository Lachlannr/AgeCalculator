# Age Calculator CLI

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A robust, dependency-free command-line tool for calculating age from a wide variety of date formats. This script features a powerful date parser, precise age calculation logic, and an interactive CLI, all built using only the Python standard library.

The tool provides a user's age in years, months, and days, and includes features like identifying the birth day of the week and a countdown to the next birthday.

## Key Features

-   **Extensive Date Format Support**: Parses 70+ formats, including:
    - Standard formats (`YYYY-MM-DD`, `MM/DD/YYYY`, `DD.MM.YYYY`)
    - Natural language (`December 25, 1990`, `25th of December 1990`)
    - Unix timestamps (`659318400`)
    - Relative dates (`today`, `yesterday`, `last year`, `next month`)
    - ISO 8601 formats (week dates, timestamps with microseconds)
    - RFC 2822 formats
    - Julian dates (`2023-359`)
    - Compact numeric (`19901225`, `251290`)
    - Year only (`1990`)
-   **Accurate Age Calculation**: Precisely calculates age in years, months, and days, correctly handling leap years and month-end boundary conditions.
-   **Rich Output**: Tells you the day of the week you were born on and provides a countdown to your next birthday.
-   **Dual-Mode CLI**: Supports both an interactive prompt and direct execution via command-line arguments.
-   **Terminal Compatibility**: Use `--no-emoji` flag for terminals that don't support emoji rendering.
-   **Zero Dependencies**: Built entirely with the Python standard library, making it highly portable and easy to run anywhere.
-   **Comprehensive Test Suite**: Includes a robust set of unit tests to ensure accuracy and reliability.

## Supported Date Formats

The Age Calculator supports an extensive range of date formats:

### Standard Formats
```
1990-12-25          # ISO 8601
12/25/1990          # US format
25.12.1990          # European format
25-12-1990          # Dash separator
```

### Natural Language
```
December 25, 1990
25 Dec 1990
Dec 25 1990
25th of December 1990
December 1st, 2000
```

### Relative Dates
```
today
yesterday
tomorrow
last week
last month
last year
next week
next month
next year
```

### Timestamps
```
659318400                    # Unix timestamp
2023-12-25T14:30:00         # ISO 8601 timestamp
2023-12-25 14:30:00         # Standard timestamp
Mon, 25 Dec 1990 12:00:00   # RFC 2822
```

### Special Formats
```
2023-359            # Julian date (YYYY-DDD)
2025-W37-2          # ISO 8601 week date
19901225            # Compact YYYYMMDD
1990                # Year only (defaults to Jan 1)
Dec 1990            # Month and year only
```

### European & International
```
25.12.1990
25-Dec-1990
25 December 1990
```

### Two-Digit Years
```
12/25/90            # Assumes 1990 (< 50 → 2000s, >= 50 → 1900s)
25.12.98            # December 25, 1998
```

## Interesting Techniques

The codebase uses several notable techniques to achieve its robustness and flexibility:

-   **Cascading Parse Strategy**: The `DateParser` in [`age_calculator.py`](./age_calculator.py) uses a cascading strategy for efficiency. It attempts to match input against cheap, highly specific parsers (e.g., Unix timestamps, relative dates like "today", Julian dates) before iterating through a broad list of standard formats.
-   **Locale-Independent Parsing**: To handle natural language dates with weekday names (e.g., "Tuesday, Sep 9, 2025"), the parser uses a regular expression to strip the weekday before parsing. This avoids reliance on system-level [`locale`](https://docs.python.org/3/library/locale.html) settings, making the tool's behavior consistent across different environments.
-   **Structured Data with Dataclasses**: The `calculate_age` function returns an `AgeResult` object, which is a [`dataclass`](https://docs.python.org/3/library/dataclasses.html). This provides a clear, type-safe structure for the output instead of relying on dictionaries.
-   **Precise Boundary Condition Handling**: The core age calculation logic correctly handles complex edge cases, such as leap-day birthdays in common years and birthdays occurring late in a month.
-   **MessageFormatter Pattern**: A dedicated `MessageFormatter` class centralizes all emoji/non-emoji message formatting, eliminating code duplication and making terminal compatibility easy to manage.

## Technology and Libraries

This project is intentionally built with **zero external dependencies**, relying solely on the Python 3 standard library.

-   [`argparse`](https://docs.python.org/3/library/argparse.html): Used to handle command-line arguments for direct execution mode.
-   [`re`](https://docs.python.org/3/library/re.html): Used extensively for pre-processing and validating user input against various date patterns.
-   [`datetime`](https://docs.python.org/3/library/datetime.html): The foundation for all date and time logic, including parsing with `strptime` and timedelta calculations.
-   [`unittest`](https://docs.python.org/3/library/unittest.html): The built-in framework used to create the comprehensive test suite in [`test_age_calculator.py`](./test_age_calculator.py), ensuring the accuracy of parsing and calculation logic.

## Project Structure

```
AgeCalculator/
├── age_calculator.py
├── LICENSE
├── README.md
└── test_age_calculator.py
```

-   **`age_calculator.py`**: The main application file, containing the logic for parsing dates and calculating age.
-   **`test_age_calculator.py`**: Contains all unit tests for the project.

## License

This project is licensed under the MIT License.
