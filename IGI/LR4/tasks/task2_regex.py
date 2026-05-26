"""Laboratory Work No. 4.

Task 2. Regular expressions and text analysis.

Variant 13:
Text analyzer:
-Get a list of hexadecimal numbers contained in the text.
-Check if there are numbers in the text followed by a "+". 
- Determine the number of words that are 4 characters long; 
- find words with the number of vowels equal to the number of consonants and their ordinal numbers; 
- output words in descending order of their length

Version: 1.5
Developer: Kruchonok Aleksandra Sergeevna
Development date: 2026-04-11
"""

# Исходные данные - из файла. 
# Получение инфы через регулярки:
# – количество предложений в тексте; 
# – количество предложений в тексте каждого вида отдельно (повествовательные, вопросительные и побудительные); 
# – среднюю длину предложения в символах (считаются только слова); 
# – среднюю длину слова в тексте в символах; 
# – количество смайликов в заданном тексте. 

# Получить список шестнадцатеричных чисел, содержащихся в тексте.
# Проверить, существуют ли в тексте цифры, за которыми стоит «+». 
# Определить число слов, длина которых равна 4 символа; 
# найти слова, у которых количество гласных равно количеству согласных и их порядковые номера; 
# вывести слова в порядке убывания их длин.

# Вывести инфу на экран и сохранить в другой файл. 
# Заархивировать файл с результатом с помощью модуля zipfile и обеспечить получение информации о файле в архиве.



# слова = hex


from __future__ import annotations

import re
import zipfile
from pathlib import Path

from utils.input_utils import ask_yes_no


OUTPUT_DIR = Path("output")

# Источник
SOURCE_FILE = OUTPUT_DIR / "task2_source_text.txt"

# Файл результата, создается и перезаписывается авто
RESULT_FILE = OUTPUT_DIR / "task2_result.txt"

# ZIP-архив результата, тоже создается и перезаписывается программой
ARCHIVE_FILE = OUTPUT_DIR / "task2_result_archive.zip"


# Hex (обычные слова (bad, face, cafe) НЕ hex)
# Явно оформленные hex-записи:
# 1) 0xFF, 0X10
# 2) AB12, 2A3, 12AF — и цифра, и буква A-F
# 3) FACEh, BEEFh, 73h — суффикс h/H
HEX_PATTERN = (
    # группа без запоминания (чтобы объединить несколько вариантов, но не возвращать саму группу отдельно)
    r"\b(?:" 
    r"0[xX][0-9A-Fa-f]+"
    # ?= это первая проверка вперед : дальше должна быть хотя бы одна буква A-F или a-f
    r"|(?=[0-9A-Fa-f]*[A-Fa-f])(?=[0-9A-Fa-f]*\d)[0-9A-Fa-f]+[hH]?"
    r"|[0-9A-Fa-f]+[hH]"
    r")\b"
)

# Проверка цифр/чисел, за которыми стоит пробел и плюс.
# Пример: "(3 + 5) - 9×4" найдено "3".
# В выражении "17+20" ничего не будет найдено, потому что нет пробела перед плюсиком.
DIGIT_BEFORE_PLUS_PATTERN = r"\b\d+(?=\s+\+)"

# Слово:
# 1) обычная последовательность русских или английских букв;
# 2) явно оформленное шестнадцатеричное число.
# Чистые числа 7, 73, 2024 не считаются.
# Выражения 9×4 и 9x4 не считаются.
WORD_PATTERN = (
    r"\b(?:"
    r"0[xX][0-9A-Fa-f]+"
    r"|(?=[0-9A-Fa-f]*[A-Fa-f])(?=[0-9A-Fa-f]*\d)[0-9A-Fa-f]+[hH]?"
    r"|[0-9A-Fa-f]+[hH]"
    r"|[A-Za-zА-Яа-яЁё]+"
    r")\b"
)

# Предложение — фрагмент текста, который заканчивается одним или несколькими
# знаками конца предложения: ".", "?", "!".
# Поэтому "!!" — это конец предложения, "??" — тоже,
# а "?!" - одновременно вопросительным и побудительным.
SENTENCE_PATTERN = r"[^.!?]+[.!?]+"

# Знаки конца предложения в самом конце найденного предложения.
ENDING_PATTERN = r"[.!?]+$"

# Смайлик по условию:
# 1) первым символом ровно один раз идет ";" или ":";
# 2) затем может идти "-" сколько угодно раз, даже 0;
# 3) затем обязательно идет одна или более одинаковых скобок:
#    "(", ")", "[", "]";
# 4) внутри смайлика нет других символов.
SMILE_PATTERN = (
    # < проверка смотрит назад, то есть на символы перед текущей позицией.
    # ! — отрицание, то есть не должно быть.
    r"(?<![;:])"   
    r"(?:;|:)"
    r"-*"
    r"(?P<bracket>[\(\)\[\]])"
    r"(?P=bracket)*"
    r"(?![\(\)\[\];:\-])"
)

# Гласные для русского и английского языков.
VOWELS = set("аеёиоуыэюяАЕЁИОУЫЭЮЯaeiouAEIOU")


def read_source_text() -> str | None:
    """Read source text from the file."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if not SOURCE_FILE.exists():
        print(f"\nSource file was not found: {SOURCE_FILE}")
        print("Create this file manually in VS Code and write text into it.")
        print("Then run task 2 again.")
        return None

    return SOURCE_FILE.read_text(encoding="utf-8")


def get_words(text: str) -> list[str]:
    """Return all words from text."""
    # re.findall возвращает все непересекающиеся совпадения.
    return re.findall(WORD_PATTERN, text)

# Cчет гласных и согласных в 1 слове
def count_vowels_and_consonants(word: str) -> tuple[int, int]:
    """Count vowels and consonants in one word."""
    vowels_count = 0
    consonants_count = 0

    for char in word:
        if char in VOWELS:
            vowels_count += 1
        elif char.isalpha():
            consonants_count += 1

    return vowels_count, consonants_count

# Одинаковое кол-во гласных и согласных
def find_words_with_equal_vowels_and_consonants(text: str) -> list[tuple[int, str]]:
    """Find words where vowels count equals consonants count."""
    result = []
    words = get_words(text)

    for index, word in enumerate(words, start=1):
        vowels_count, consonants_count = count_vowels_and_consonants(word)

        # vowels_count > 0 нужно, чтобы не считать слова без гласных.
        # hex "FF" не должен попадать как слово с 0 гласных и 0 согласных.
        if vowels_count == consonants_count and vowels_count > 0:
            result.append((index, word))

    return result


def analyze_sentences(text: str) -> dict[str, float | int]:
    """Analyze sentence statistics."""
    sentences = re.findall(SENTENCE_PATTERN, text)

    narrative_count = 0
    question_count = 0
    imperative_count = 0

    # Здесь будут храниться количества слов в каждом предложении.
    # [5, 3, 7]: в первом предложении 5 слов, во втором 3, в третьем 7.
    words_count_in_sentences = []

    # Здесь будут храниться длины всех слов текста (слово "tree" даст длину 4)
    word_lengths = []

    for sentence in sentences:
        clear_sentence = sentence.strip()

        # Ищем знаки конца предложения: ".", "!", "!!", "?", "??", "?!"
        ending_match = re.search(ENDING_PATTERN, clear_sentence)

        if ending_match:
            ending = ending_match.group(0)

            # Повествовательное: заканчивается точкой и не содержит вопросительного или восклицательного знака.
            if "." in ending and "?" not in ending and "!" not in ending:
                narrative_count += 1

            # Вопросительное: в конце есть вопросительный знак.
            # "??" и "?!" считается вопросительным.
            if "?" in ending:
                question_count += 1

            # Побудительное: в конце есть восклицательный знак.
            # "!!" и "?!" считается побудительным.
            if "!" in ending:
                imperative_count += 1

        # Получаем слова конкретного предложения.
        words_in_sentence = get_words(clear_sentence)

        # Для средней длины предложения считаем количество слов в этом предложении.
        words_count_in_sentences.append(len(words_in_sentence))

        # Для средней длины слова сохраняем длину каждого найденного слова.
        for word in words_in_sentence:
            word_lengths.append(len(word))

    # Средняя длина предложения: сумма слов по предложениям / количество предложений.
    average_sentence_length = (
        sum(words_count_in_sentences) / len(words_count_in_sentences)
        if words_count_in_sentences
        else 0
    )

    # Средняя длина слова: сумма длин всех слов / количество слов.
    average_word_length = (
        sum(word_lengths) / len(word_lengths)
        if word_lengths
        else 0
    )

    return {
        "total_sentences": len(sentences),
        "narrative_sentences": narrative_count,
        "question_sentences": question_count,
        "imperative_sentences": imperative_count,
        "average_sentence_length_in_words": round(average_sentence_length, 2),
        "average_word_length_in_chars": round(average_word_length, 2),
    }

def find_smiles(text: str) -> list[str]:
    """Find full smile strings in text."""
    # Используем finditer, потому что в регулярке есть именованная группа.
    # match.group(0) возвращает полное найденное совпадение.
    return [match.group(0) for match in re.finditer(SMILE_PATTERN, text)]


def build_report(text: str) -> str:
    """Build final text analysis report."""
    # 1. Список шестнадцатеричных чисел.
    hex_numbers = re.findall(HEX_PATTERN, text)

    # 2. Проверка, есть ли число, после которого стоит пробел и плюс.
    # search нужен для ответа "существует / не существует".
    digit_before_plus_exists = re.search(DIGIT_BEFORE_PLUS_PATTERN, text) is not None

    # findall нужен, чтобы вывести все такие числа.
    digits_before_plus = re.findall(DIGIT_BEFORE_PLUS_PATTERN, text)

    # 3. Все слова по правилу задачи.
    words = get_words(text)

    # 4. Слова длиной 4 символа.
    four_letter_words = [word for word in words if len(word) == 4]

    # 5. Слова, у которых количество гласных равно количеству согласных.
    equal_vowel_consonant_words = find_words_with_equal_vowels_and_consonants(text)

    # 6. Слова в порядке убывания длины.
    words_sorted_by_length = sorted(
        set(words),
        key=lambda word: (-len(word), word.lower()),
    )

    # 7. Анализ предложений.
    sentence_stats = analyze_sentences(text)

    # 8. Смайлики.
    smiles = find_smiles(text)

    # re.sub — замена: все hex-числа заменяем на три буквы HEX.
    text_after_sub = re.sub(HEX_PATTERN, "HEX", text)

    # re.split — разделение текста по знакам конца предложения.
    split_sentences = [
        part.strip()
        for part in re.split(r"[.!?]+", text)
        if part.strip()
    ]

    lines = [
        "Task 2. Regular expression analysis",
        "Developer: Kruchonok Aleksandra Sergeevna",
        "Development date: 2026-04-11",
        "=" * 80,
        "\nSource text:",
        text,
        "\n1. Hexadecimal numbers:",
        str(hex_numbers),
        "\n2. Numbers followed by space and plus:",
        str(digits_before_plus),
        f"Exist: {'yes' if digit_before_plus_exists else 'no'}",
        "\n3. Words with length equal to 4:",
        str(four_letter_words),
        f"Count: {len(four_letter_words)}",
        "\n4. Words where vowels count equals consonants count:",
        str(equal_vowel_consonant_words),
        "\n5. Words sorted by length descending:",
        str(words_sorted_by_length),
        "\n6. Sentence statistics:",
    ]

    for key, value in sentence_stats.items():
        lines.append(f"{key}: {value}")

    lines.extend(
        [
            "\n7. Smiles:",
            str(smiles),
            f"Smile count: {len(smiles)}",
            "\nText after re.sub: hexadecimal numbers replaced with HEX:",
            text_after_sub,
            "\nSentences after re.split:",
            str(split_sentences),
        ]
    )

    return "\n".join(lines)


def save_report(report: str) -> None:
    """Save report to result file."""
    # write_text перезаписывает файл результата при каждом запуске.
    RESULT_FILE.write_text(report, encoding="utf-8")


def create_archive() -> None:
    """Create ZIP archive with result file and print archive information."""
    # mode="w" перезаписывает архив при каждом запуске.
    # ZIP_DEFLATED вкл сжатие, compresslevel=9 - макс степень сжатия.
    with zipfile.ZipFile(
        ARCHIVE_FILE,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as archive:
        # добавление файла
        archive.write(RESULT_FILE, arcname=RESULT_FILE.name)

    # getinfo получает информацию о файле внутри архива без извлечения.
    with zipfile.ZipFile(ARCHIVE_FILE, mode="r") as archive:
        file_info = archive.getinfo(RESULT_FILE.name)

        original_size = file_info.file_size
        compressed_size = file_info.compress_size

        compression_percent = (
            (1 - compressed_size / original_size) * 100
            if original_size
            else 0
        )

        print("\nArchive information:")
        print(f"Archive: {ARCHIVE_FILE}")
        print(f"File in archive: {file_info.filename}")
        print(f"Original size: {original_size} bytes")
        print(f"Compressed size: {compressed_size} bytes")
        print(f"Compression percent: {compression_percent:.2f}%")
        print(f"Compression method code: {file_info.compress_type}")


def run_task_2() -> None:
    """Run task 2."""
    while True:
        print("\nTask 2. Regular expressions.")
        print("Developer: Kruchonok Aleksandra Sergeevna")
        print("Development date: 2026-04-11")

        text = read_source_text()

        if text is None:
            if not ask_yes_no("\nRepeat task 2? (y/n): "):
                break
            continue

        report = build_report(text)
        save_report(report)

        print("\n" + report)

        create_archive()

        print(f"\nSource file: {SOURCE_FILE}")
        print(f"Result file: {RESULT_FILE}")
        print(f"Archive file: {ARCHIVE_FILE}")

        if not ask_yes_no("\nRepeat task 2? (y/n): "):
            break