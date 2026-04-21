"""Business logic for task 1: power series calculation.

Lab 3
Title: Standard Data Types, Collections, Functions, and Modules
Version: 1.1
Developer: Kruchonok Aleksandra Sergeevna
Development date: 2026-03-29
"""

import math
from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

from utils.decorators import log_execution
from utils.input_utils import ask_float, ask_positive_float, ask_yes_no


MAX_ITERATIONS = 500
P = ParamSpec("P")
R = TypeVar("R")


def table_header_decorator(func: Callable[P, R]) -> Callable[P, R]:
    """Print table headers before the decorated result function.

    Args:
        func: Wrapped function.

    Returns:
        A wrapper that prints the table header before calling func.
    """

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print("\nResult:")
        print("-" * 70)
        print(f"{'x':>12} {'n':>8} {'F(x)':>18} {'Math F(x)':>18} {'eps':>12}")
        print("-" * 70)
        return func(*args, **kwargs)

    return wrapper


def is_valid_x(x: float) -> bool:
    """Check whether x belongs to the convergence interval.

    Args:
        x: Function argument.

    Returns:
        True if -1 < x < 1, otherwise False.
    """
    return -1 < x < 1


def calculate_ln_series(
    x: float,
    eps: float,
    max_iterations: int = MAX_ITERATIONS,
) -> tuple[float, int]:
    """Calculate ln(1 + x) using the power series.

    The series is valid for |x| < 1:
        ln(1 + x) = x - x^2 / 2 + x^3 / 3 - ...

    Args:
        x: Function argument.
        eps: Required calculation precision.
        max_iterations: Maximum allowed number of terms.

    Returns:
        A tuple with the series value and the number of used terms.

    Raises:
        ValueError: If x is outside the convergence interval or eps is invalid.
        OverflowError: If the required precision is not reached in time.
    """
    if not is_valid_x(x):
        raise ValueError("For this series, x must satisfy -1 < x < 1.")
    if eps <= 0:
        raise ValueError("eps must be positive.")

    term = x
    series_sum = 0.0
    n = 0

    while abs(term) >= eps and n < max_iterations:
        series_sum += term
        n += 1
        term *= -x * n / (n + 1)

    if abs(term) >= eps:
        raise OverflowError(
            "Failed to reach the required precision "
            f"in {max_iterations} iterations."
        )

    return series_sum, n


@table_header_decorator
def print_result_row(
    x: float,
    terms_count: int,
    series_value: float,
    math_value: float,
    eps: float,
) -> None:
    """Print the calculation result row in tabular format.

    Args:
        x: Function argument.
        terms_count: Number of used terms.
        series_value: Value obtained from the power series.
        math_value: Value obtained using the math module.
        eps: Required calculation precision.
    """
    print(
        f"{x:>12.6f} {terms_count:>8} "
        f"{series_value:>18.10f} {math_value:>18.10f} {eps:>12.2e}"
    )


@log_execution
def run_task_1() -> None:
    """Run the interactive interface for task 1."""
    while True:
        print("\nTask 1. Calculate ln(1 + x) using the power series.")

        while True:
            x = ask_float("Enter x (-1 < x < 1): ")
            if is_valid_x(x):
                break
            print("Input error: x must satisfy -1 < x < 1.")

        eps = ask_positive_float("Enter eps (> 0): ")

        try:
            series_value, terms_count = calculate_ln_series(x, eps)
            math_value = math.log(1 + x)
            print_result_row(x, terms_count, series_value, math_value, eps)
        except OverflowError as error:
            print(f"Calculation error: {error}")

        if not ask_yes_no("\nDo you want to repeat task 1? (yes/no): "):
            break