# Age Calculator

This project provides a command-line tool for calculating age from a birthdate. It is written in Python and designed to be a flexible and robust date-parsing and age-calculation engine. The tool handles a wide variety of date formats, including natural language.

The core logic is encapsulated in two main classes: `DateParser` for interpreting input strings and `AgeCalculator` for performing the age calculation. The project includes a comprehensive test suite built with Python's `unittest` framework.

## Interesting Techniques

The codebase uses several notable techniques:

- **Flexible Date Parsing**: The `DateParser` class in [`age_calculator.py`](./age_calculator.py) uses a series of parsing strategies to handle multiple date formats without external dependencies. It attempts to parse formats in a specific order, from most common to least common, to resolve ambiguity.
- **Pre-compiled Regular Expressions**: To improve performance when handling dates with ordinal suffixes (e.g., "1st", "2nd"), the script pre-compiles the regular expression using [`re.compile()`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/RegExp/compile).
- **Robust Age Calculation**: The `calculate_age` method in [`age_calculator.py`](./age_calculator.py) correctly accounts for leap years and the varying number of days in each month.
- **Mocking for Tests**: The test file, [`Test.py`](./Test.py), uses [`unittest.mock.patch`](https://docs.python.org/3/library/unittest.mock.html#unittest.mock.patch) to control the "current" date for tests, ensuring that tests are repeatable and not dependent on when they are run.

## Technologies and Libraries

This project intentionally limits its external dependencies, relying on Python's standard library.

- **[datetime](https://docs.python.org/3/library/datetime.html)**: Used for all date and time manipulation.
- **[re](https://docs.python.org/3/library/re.html)**: Used for parsing date strings with ordinal numbers.
- **[unittest](https://docs.python.org/3/library/unittest.html)**: The standard Python framework for unit testing, used extensively in [`Test.py`](./Test.py).

## Project Structure

```
age-calculator/
├── .gitignore
├── age_calculator.py
├── LICENSE
├── README.md
└── Test.py
```

- **`age_calculator.py`**: The main application file, containing the logic for parsing dates and calculating age.
- **`Test.py`**: Contains all unit tests for the project.