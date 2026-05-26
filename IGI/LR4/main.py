"""Main module for Laboratory Work No. 4.

Laboratory work title:
"Working with files, classes, serializers, regular expressions and standard libraries"

Version: 1.6
Developer: Kruchonok Aleksandra Sergeevna
Development date: 2026-04-22
"""

from tasks.task1_files import run_task_1
from tasks.task2_regex import run_task_2
from tasks.task3_plots import run_task_3
from tasks.task4_triangle import run_task_4
from tasks.task5_NumPy import run_task_5
from tasks.task6_Pandas import run_task_6
from utils.input_utils import ask_int_in_range


def show_menu() -> None:
    """Display the main application menu."""
    print("\n" + "=" * 80)
    print("Laboratory work No. 4")
    print("Theme: Working with files, classes, serializers, regular expressions")
    print("Developer: Kruchonok Aleksandra Sergeevna")
    print("=" * 80)
    print("1. Task 1 - CSV, pickle, zipfile, exported goods")
    print("2. Task 2 - Regular expressions and text analysis")
    print("3. Task 3 - ln(1 + x), class, statistics and matplotlib")
    print("4. Task 4 - Triangle class hierarchy and drawing")
    print("5. Task 5 - NumPy matrix processing")
    print("6. Task 6 - Pandas IMDB dataset analysis")
    print("0. Exit")
    print("=" * 80)


def main() -> None:
    """Start the menu-driven application."""
    actions = {
        1: run_task_1,
        2: run_task_2,
        3: run_task_3,
        4: run_task_4,
        5: run_task_5,
        6: run_task_6,
    }

    while True:
        show_menu()

        choice = ask_int_in_range("Choose task number: ", 0, 6)

        if choice == 0:
            print("Program finished. Goodbye!")
            break

        try:
            actions[choice]()
        except KeyboardInterrupt:
            print("\nTask interrupted by user. Returning to main menu.")
        except Exception as error:
            print(f"Unexpected error: {error}")


if __name__ == "__main__":
    main()