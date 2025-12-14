# Age Calculator

A command-line tool for calculating ages from 100+ international date formats. Zero dependencies—built with Python's standard library.

Handles natural language dates, Unix timestamps, Excel serial numbers, Julian dates, and international formats. Provides both CLI and programmatic interfaces.

## Features

**Date Formats**

- Standard: ISO 8601, US (`MM/DD/YYYY`), European (`DD.MM.YYYY`)
- Natural language: `December 25, 1990`, `25th of December 1990`
- Timestamps: Unix, ISO 8601 with microseconds, RFC 2822
- Specialized: Julian dates (`2023-359`), Excel serials (`36526`), fiscal quarters (`2023-Q4`)
- Relative: `today`, `yesterday`, `last year`
- Compact numeric: `19901225`, `251290`

**Calculation**

- Precise age in years, months, and days
- Leap year handling for February 29th birthdays
- Month-end boundary support (Jan 31 → Feb 28/29)
- Metadata: birth day of week, total days lived, next birthday countdown

## Interesting Techniques

**Multi-strategy date parsing**: The [`DateParser`](age_calculator.py) class chains multiple parsing strategies—[`strptime`](https://docs.python.org/3/library/datetime.html#datetime.datetime.strptime) format strings, regex extraction, and specialized parsers for Unix timestamps and Excel serial numbers. When standard parsing fails, it falls back through increasingly permissive strategies.

**Walrus operator for control flow**: Uses Python 3.8's [assignment expressions](https://docs.python.org/3/whatsnew/3.8.html#assignment-expressions) to attempt multiple date formats in sequence, returning on first successful parse:
