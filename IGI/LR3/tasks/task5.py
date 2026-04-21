"""Business logic for task 5: processing a float list.

Lab 3
Title: Standard Data Types, Collections, Functions, and Modules
Version: 1
Developer: Kruchonok Aleksandra Sergeevna
Development date: 2026-04-02
"""

from utils.data_init import (
    create_list_iterator,
    fill_list_by_user,
    fill_list_with_generator,
)
from utils.decorators import log_execution
from utils.input_utils import ask_int_in_range, ask_yes_no


MIN_LIST_SIZE = 1
MAX_LIST_SIZE = 100


def sum_at_odd_indices(values: list[float]) -> float:
    """Calculate the sum of elements with odd indices.

    In Python, list indices start from 0, so odd indices are 1, 3, 5, ...

    Args:
        values: Source list.

    Returns:
        The sum of elements with odd indices.
    """
    return sum(values[1::2])


def first_negative_index(values: list[float]) -> int | None:
    """Find the index of the first negative element.

    Args:
        values: Source list.

    Returns:
        The index of the first negative element or None.
    """
    for index, value in enumerate(values):
        if value < 0:
            return index
    return None


def last_negative_index(values: list[float]) -> int | None:
    """Find the index of the last negative element.

    Args:
        values: Source list.

    Returns:
        The index of the last negative element or None.
    """
    for index in range(len(values) - 1, -1, -1):
        if values[index] < 0:
            return index
    return None


def sum_between_first_and_last_negative(values: list[float]) -> float | None:
    """Calculate the sum of elements between the first and last negatives.

    The first and last negative elements themselves are not included.

    Args:
        values: Source list.

    Returns:
        The sum of elements between the first and last negative elements,
        or None if there are fewer than two negative elements.
    """
    first_index = first_negative_index(values)
    last_index = last_negative_index(values)

    if first_index is None or last_index is None or first_index == last_index:
        return None

    return sum(values[first_index + 1:last_index])


def print_list(values: list[float]) -> None:
    """Print the list in a friendly format.

    Args:
        values: Source list.
    """
    iterator = create_list_iterator(values)
    formatted_values = ", ".join(f"{value:.2f}" for value in iterator)
    print(f"List: {formatted_values}")


@log_execution
def run_task_5() -> None:
    """Run the interactive interface for task 5."""
    while True:
        print("\nTask 5. Process a float list.")

        size = ask_int_in_range(
            "Enter list size (1..100): ",
            MIN_LIST_SIZE,
            MAX_LIST_SIZE,
        )

        print("\nChoose initialization method:")
        print("1. User input")
        print("2. Generator function")

        method = ask_int_in_range("Your choice: ", 1, 2)

        if method == 1:
            values = fill_list_by_user(size)
        else:
            values = fill_list_with_generator(size)

        print_list(values)

        odd_indices_sum = sum_at_odd_indices(values)
        between_negatives_sum = sum_between_first_and_last_negative(values)

        print(f"Sum of elements with odd indices: {odd_indices_sum:.2f}")

        if between_negatives_sum is None:
            print("There are not enough negative elements for the second sum.")
        else:
            print(
                "Sum of elements between the first and last negative elements: "
                f"{between_negatives_sum:.2f}"
            )

        if not ask_yes_no("\nDo you want to repeat task 5? (yes/no): "):
            break