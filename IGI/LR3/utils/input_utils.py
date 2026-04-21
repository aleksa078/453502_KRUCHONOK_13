# Валидация пользовательского ввода и обработка ошибок ввода.

"""Utility functions for validated user input.

Lab 3
Title: Standard Data Types, Collections, Functions, and Modules
Version: 1.1
Developer: Kruchonok Aleksandra Sergeevna
Development date: 2026-04-01
"""


def ask_int(prompt: str) -> int:
    """Read an integer from the user with validation.

    Args:
        prompt: Text shown to the user.

    Returns:
        A valid integer.
    """
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Invalid input. Please enter an integer.")


def ask_float(prompt: str) -> float:
    """Read a float from the user with validation.

    Args:
        prompt: Text shown to the user.

    Returns:
        A valid float number.
    """
    w

def ask_positive_float(prompt: str) -> float:
    """Read a positive float from the user with validation.

    Args:
        prompt: Text shown to the user.

    Returns:
        A positive float value.
    """
    while True:
        value = ask_float(prompt)
        if value > 0:
            return value
        print("The number must be positive.")


def ask_int_in_range(prompt: str, min_value: int, max_value: int) -> int:
    """Read an integer in the specified range.

    Args:
        prompt: Text shown to the user.
        min_value: Minimum allowed value.
        max_value: Maximum allowed value.

    Returns:
        A valid integer from the specified range.
    """
    while True:
        value = ask_int(prompt)
        if min_value <= value <= max_value:
            return value
        print(f"Please enter a value from {min_value} to {max_value}.")


def ask_yes_no(prompt: str) -> bool:
    """Ask a yes/no question and return True for yes and False for no.

    Args:
        prompt: Text shown to the user.

    Returns:
        True if the user answered yes, otherwise False.
    """
    while True:
        answer = input(prompt).strip().lower()

        if answer in {"y", "yes", "д", "да"}:
            return True
        if answer in {"n", "no", "н", "нет"}:
            return False

        print("Invalid input. Please enter yes/no.")