"""Business logic for task 4: text analysis.

Lab 3
Title: Standard Data Types, Collections, Functions, and Modules
Version: 1.1
Developer: Kruchonok Aleksandra Sergeevna
Development date: 2026-03-31
"""

from utils.decorators import log_execution
from utils.input_utils import ask_yes_no


TEXT = (
    "So she was considering in her own mind, as well as she could, "
    "for the hot day made her feel very sleepy and stupid, whether "
    "the pleasure of making a daisy-chain would be worth the trouble "
    "of getting up and picking the daisies, when suddenly a White "
    "Rabbit with pink eyes ran close by her."
)

PUNCTUATION = ".,!?;:-\"'()[]{}"


def normalize_word(word: str) -> str:
    """Remove punctuation from word edges and convert it to lowercase.

    Args:
        word: Source word.

    Returns:
        A cleaned lowercase word.
    """
    return word.strip(PUNCTUATION).lower()


def extract_words(text: str) -> list[str]:
    """Extract normalized words from a text without regular expressions.

    Args:
        text: Source text.

    Returns:
        A list of normalized words.
    """
    prepared_text = text.replace(",", " ")
    raw_words = prepared_text.split()

    words = []
    for raw_word in raw_words:
        cleaned_word = normalize_word(raw_word)
        if cleaned_word:
            words.append(cleaned_word)

    return words


def count_letters(word: str) -> int:
    """Count only alphabetic characters in a word.

    Args:
        word: Source word.

    Returns:
        Number of alphabetic characters.
    """
    return sum(1 for char in word if char.isalpha())


def words_with_odd_length(words: list[str]) -> list[str]:
    """Find all words with an odd number of letters.

    Args:
        words: A list of words.

    Returns:
        A list of matching words.
    """
    return [word for word in words if count_letters(word) % 2 == 1]


def find_shortest_word_starting_with_i(words: list[str]) -> str | None:
    """Find the shortest word that starts with the letter 'i'.

    Args:
        words: A list of words.

    Returns:
        The shortest matching word or None if there is no such word.
    """
    matching_words = [word for word in words if word.startswith("i")]
    if not matching_words:
        return None

    return min(matching_words, key=count_letters)


def find_repeated_words(words: list[str]) -> list[str]:
    """Find repeated words in the text.

    Args:
        words: A list of words.

    Returns:
        A sorted list of unique repeated words.
    """
    counts: dict[str, int] = {}

    for word in words:
        counts[word] = counts.get(word, 0) + 1

    return sorted(word for word, count in counts.items() if count > 1)


@log_execution
def run_task_4() -> None:
    """Run the interactive interface for task 4."""
    while True:
        print("\nTask 4. Text analysis.")
        print("\nSource text:")
        print(TEXT)

        words = extract_words(TEXT)
        odd_words = words_with_odd_length(words)
        shortest_i_word = find_shortest_word_starting_with_i(words)
        repeated_words = find_repeated_words(words)

        print("\nAnalysis results:")
        print(f"Total number of words: {len(words)}")
        print(f"Words with odd number of letters: {', '.join(odd_words)}")
        print(
            "Shortest word starting with 'i': "
            f"{shortest_i_word if shortest_i_word is not None else 'not found'}"
        )
        print(
            "Repeated words: "
            f"{', '.join(repeated_words) if repeated_words else 'not found'}"
        )

        if not ask_yes_no("\nDo you want to repeat task 4? (yes/no): "):
            break