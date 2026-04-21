"""Business logic for task 2: counting natural numbers.

Lab 3
Title: Standard Data Types, Collections, Functions, and Modules
Version: 1
Developer: Kruchonok Aleksandra Sergeevna
Development date: 2026-03-29
"""

from collections.abc import Iterable

from utils.data_init import generate_numbers_until_zero
from utils.decorators import log_execution
from utils.input_utils import ask_yes_no


def count_natural_numbers(numbers: Iterable[int]) -> tuple[int, list[int]]:
    """Count natural numbers in the provided sequence.

    Args:
        numbers: Any iterable with integer values.

    Returns:
        A tuple with the count of natural numbers and the entered values.
    """
    entered_numbers: list[int] = []
    natural_count = 0

    for number in numbers:
        entered_numbers.append(number)
        if number > 0:
            natural_count += 1

    return natural_count, entered_numbers


@log_execution
def run_task_2() -> None:
    """Run the interactive interface for task 2."""
    while True:
        print("\nTask 2. Count natural numbers in the entered sequence.")

        number_generator = generate_numbers_until_zero()
        result, numbers = count_natural_numbers(number_generator)

        print(f"Entered numbers: {numbers}")
        print(f"Count of natural numbers: {result}")

        if not ask_yes_no("\nDo you want to repeat task 2? (yes/no): "):
            break