# Инициализация данных, генераторы и создание итератора.

"""Functions for sequence initialization.

Lab 3
Title: Standard Data Types, Collections, Functions, and Modules
Version: 1.1
Developer: Kruchonok Aleksandra Sergeevna
Development date: 2026-03-30
"""

import random
from collections.abc import Generator, Iterator

from utils.input_utils import ask_float, ask_int


RANDOM_MIN_VALUE = -10.0
RANDOM_MAX_VALUE = 10.0
RANDOM_PRECISION = 2


def fill_list_by_user(size: int) -> list[float]:
    """Initialize a float list using user input.

    Args:
        size: Required list size.

    Returns:
        A filled list of float values.
    """
    values: list[float] = []

    for index in range(size):
        value = ask_float(f"Enter element #{index + 1}: ")
        values.append(value)

    return values


def generate_random_float_values(size: int) -> Generator[float, None, None]:
    """Generate float values one by one using ``yield``.

    This function is a generator function. After it is called, Python creates
    a generator object, which can be used as an iterator.

    Args:
        size: Required number of generated elements.

    Yields:
        Random float values rounded to two decimal places.
    """
    for _ in range(size):
        yield round(
            random.uniform(RANDOM_MIN_VALUE, RANDOM_MAX_VALUE),
            RANDOM_PRECISION,
        )


def fill_list_with_generator(size: int) -> list[float]:
    """Initialize a float list using a generator function.

    Args:
        size: Required list size.

    Returns:
        A filled list of generated float values.
    """
    return list(generate_random_float_values(size))


def create_list_iterator(values: list[float]) -> Iterator[float]:
    """Create an iterator object for the provided list.

    Args:
        values: Source list.

    Returns:
        A list iterator object.
    """
    return iter(values)


def generate_numbers_until_zero() -> Generator[int, None, None]:
    """Generate integers entered by the user until zero is entered.

    The terminating zero is not included in the generated sequence.

    Yields:
        Entered integers except the final zero.
    """
    print("Enter integers one by one. Enter 0 to finish.")

    while True:
        number = ask_int("Enter an integer: ")
        if number == 0:
            break
        yield number