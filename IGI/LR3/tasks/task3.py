"""Business logic for task 3: octal string analysis.

Lab 3
Title: Standard Data Types, Collections, Functions, and Modules
Version: 1.4
Developer: Kruchonok Aleksandra Sergeevna
Development date: 2026-03-30
"""

from utils.decorators import log_execution
from utils.input_utils import ask_yes_no


OCTAL_DIGITS = set("01234567")


def is_octal_string(text: str) -> bool:
    """Check whether the given string is an octal number.

    Regular expressions are not used.

    Args:
        text: Source string entered by the user.

    Returns:
        True if the string is an octal number, otherwise False.
    """
    if not text:
        return False

    return all(char in OCTAL_DIGITS for char in text)


@log_execution
def run_task_3() -> None:
    """Run the interactive interface for task 3."""
    while True:
        print("\nTask 3. Check whether the entered string is an octal number.")

        user_text = input("Enter a string: ").strip()

        if is_octal_string(user_text):
            print("The entered string is an octal number.")
        else:
            print("The entered string is NOT an octal number.")

        if not ask_yes_no("\nDo you want to repeat task 3? (yes/no): "):
            break