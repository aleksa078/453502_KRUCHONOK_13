"""Input utility functions for Lab 4.

Lab title:
"Working with files, classes, serializers, regular expressions and standard libraries"

Version: 1.1
Developer: Kruchonok Aleksandra Sergeevna
Development date: 2026-04-10
"""

from __future__ import annotations


def ask_yes_no(message: str) -> bool:
    """Ask the user a yes/no question.

    Args:
        message: Text displayed to the user.

    Returns:
        True if the user enters 'y' or 'yes', otherwise False.
    """
    while True:
        value = input(message).strip().lower()

        if value in {"Y", "y", "yes", "д", "да"}:
            return True

        if value in {"N", "n", "no", "н", "нет"}:
            return False

        print("Input error: enter y/n.")


def ask_int(message: str) -> int:
    """Read an integer value from the keyboard.

    Args:
        message: Text displayed to the user.

    Returns:
        Integer value entered by the user.
    """
    while True:
        try:
            return int(input(message).strip())
        except ValueError:
            print("Input error: enter an integer number.")


def ask_int_in_range(message: str, min_value: int, max_value: int) -> int:
    """Read an integer value from the selected range.

    Args:
        message: Text displayed to the user.
        min_value: Minimum allowed value.
        max_value: Maximum allowed value.

    Returns:
        Correct integer value.
    """
    while True:
        value = ask_int(message)

        if min_value <= value <= max_value:
            return value

        print(f"Input error: enter a number from {min_value} to {max_value}.")


def ask_float(message: str) -> float:
    """Read a float value from the keyboard.

    Args:
        message: Text displayed to the user.

    Returns:
        Float value entered by the user.
    """
    while True:
        try:
            return float(input(message).strip().replace(",", "."))
        except ValueError:
            print("Input error: enter a real number.")


def ask_positive_float(message: str) -> float:
    """Read a positive float value from the keyboard.

    Args:
        message: Text displayed to the user.

    Returns:
        Positive float value.
    """
    while True:
        value = ask_float(message)

        if value > 0:
            return value

        print("Input error: value must be positive.")


def ask_non_empty_string(message: str) -> str:
    """Read a non-empty string from the keyboard.

    Args:
        message: Text displayed to the user.

    Returns:
        Non-empty string.
    """
    while True:
        value = input(message).strip()

        if value:
            return value

        print("Input error: value cannot be empty.")