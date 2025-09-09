# Age Calculator CLI

![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A robust, dependency-free command-line tool for calculating age from a wide variety of date formats. This script features a powerful date parser, precise age calculation logic, and an interactive CLI, all built using only the Python standard library.

The tool provides a user's age in years, months, and days, and includes features like identifying the birth day of the week and a countdown to the next birthday.

## Key Features

-   **Vast Date Format Support**: Parses dozens of formats, including standard (`YYYY-MM-DD`), natural language (`December 25, 1990`), timestamps, ISO 8601 week dates, and more.
-   **Accurate Age Calculation**: Precisely calculates age in years, months, and days, correctly handling leap years and month-end boundary conditions.
-   **Rich Output**: Tells you the day of the week you were born on and provides a countdown to your next birthday.
-   **Zero Dependencies**: Built entirely with the Python standard library, making it highly portable and easy to run anywhere.
-   **Interactive CLI**: A simple and user-friendly command-line interface for entering dates.
-   **Comprehensive Test Suite**: Includes a robust set of unit tests to ensure accuracy and reliability.

## Interesting Techniques

The codebase uses several notable techniques to achieve its robustness and flexibility:

-   **Cascading Parse Strategy**: The `DateParser` in [`age_calculator.py`](./age_calculator.py) uses a cascading strategy for efficiency. It attempts to match input against cheap, highly specific parsers (e.g., relative dates like "today", Julian dates) before iterating through a broad list of standard formats.
-   **Locale-Independent Parsing**: To handle natural language dates with weekday names (e.g., "Tuesday, Sep 9, 2025"), the parser uses a regular expression to strip the weekday before parsing. This avoids reliance on system-level [`locale`](https://docs.python.org/3/library/locale.html) settings, making the tool's behavior consistent across different environments.
-   **Structured Data with Dataclasses**: The `calculate_age` function returns an `AgeResult` object, which is a [`dataclass`](https://docs.python.org/3/library/dataclasses.html). This provides a clear, type-safe structure for the output instead of relying on dictionaries.
-   **Precise Boundary Condition Handling**: The core age calculation logic correctly handles complex edge cases, such as leap-day birthdays in common years and birthdays occurring late in a month.

## Technology and Libraries

This project is intentionally built with **zero external dependencies**, relying solely on the Python 3 standard library for maximum portability.

-   [`re`](https://docs.python.org/3/library/re.html): Used extensively for pre-processing and validating user input against various date patterns.
-   [`datetime`](https://docs.python.org/3/library/datetime.html): The foundation for all date and time logic, including parsing with `strptime` and timedelta calculations.
-   [`unittest`](https://docs.python.org/3/library/unittest.html): The built-in framework used to create the comprehensive test suite in [`Test.py`](./Test.py), ensuring the accuracy of parsing and calculation logic.

## Project Structure

```
age-calculator/
├── .gitignore
├── age_calculator.py
├── LICENSE
├── README.md
└── Test.py
```

-   **`age_calculator.py`**: The main application file, containing the logic for parsing dates and calculating age.
-   **`Test.py`**: Contains all unit tests for the project.

## License

This project is licensed under the MIT License.
