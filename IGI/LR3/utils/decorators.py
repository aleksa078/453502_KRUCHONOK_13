# Общие декораторы.

"""Decorators used in the project.

Lab 3
Title: Standard Data Types, Collections, Functions, and Modules
Version: 1
Developer: Kruchonok Aleksandra Sergeevna
Development date: 2026-03-31
"""

from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar


P = ParamSpec("P")
R = TypeVar("R")


def log_execution(func: Callable[P, R]) -> Callable[P, R]:
    """Display service messages before and after function execution.

    Args:
        func: Wrapped function.

    Returns:
        A wrapper function with the same signature as the original one.
    """

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print("\n" + "-" * 70)
        print(f"Running: {func.__name__}")
        print("-" * 70)
        result = func(*args, **kwargs)
        print("-" * 70)
        print(f"Completed: {func.__name__}")
        print("-" * 70)
        return result

    return wrapper