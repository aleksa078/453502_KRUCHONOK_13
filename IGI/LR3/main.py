"""Main module for lab 3.

Laboratory work title:
"Standard Data Types, Collections, Functions, and Modules"

Version: 2
Developer: Kruchonok Aleksandra Sergeevna
Development date: 2026-03-31
"""

from tasks.task1 import run_task_1
from tasks.task2 import run_task_2
from tasks.task3 import run_task_3
from tasks.task4 import run_task_4
from tasks.task5 import run_task_5
from utils.input_utils import ask_int_in_range


MENU_MIN_OPTION = 0
MENU_MAX_OPTION = 5


def show_menu() -> None:
    """Display the main application menu."""
    print("\n" + "=" * 70)
    print("Laboratory work No. 3")
    print("Standard Data Types, Collections, Functions, and Modules")
    print("=" * 70)
    print("1. Task 1 - Power series")
    print("2. Task 2 - Count natural numbers")
    print("3. Task 3 - Check octal number")
    print("4. Task 4 - Text analysis")
    print("5. Task 5 - Float list processing")
    print("0. Exit")


def main() -> None:
    """Start the menu-driven laboratory work application."""
    actions = {
        1: run_task_1,
        2: run_task_2,
        3: run_task_3,
        4: run_task_4,
        5: run_task_5,
    }

    while True:
        show_menu()
        choice = ask_int_in_range(
            "Choose an option: ",
            MENU_MIN_OPTION,
            MENU_MAX_OPTION,
        )

        if choice == 0:
            print("Goodbye!")
            break

        try:
            actions[choice]()
        except KeyboardInterrupt:
            print("\nProgram interrupted by user. Returning to main menu.")


if __name__ == "__main__":
    main()