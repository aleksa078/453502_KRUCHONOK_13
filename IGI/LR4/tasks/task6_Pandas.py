""" Laboratory Work No. 4.

Task 6. Pandas Series and DataFrame analysis.

Variant 13: 
Analysing of IMDB Dataset of 50K Movie Reviews

Version: 1.5
Developer: Kruchonok Aleksandra Sergeevna
Development date: 2026-04-21
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from utils.input_utils import ask_yes_no


DATA_FILE = Path("data") / "IMDB Dataset.csv"
OUTPUT_DIR = Path("output")
RESULT_FILE = OUTPUT_DIR / "task6_pandas_result.txt"


def load_dataset(filename: Path) -> pd.DataFrame:
    """Load the IMDB dataset from CSV file."""
    if not filename.exists():
        raise FileNotFoundError(
            f"Файл датасета не найден: {filename}. "
            "Нужно скачать IMDB Dataset.csv и положить его в папку data."
        )

    # pd.read_csv считывает CSV-файл и возвращает DataFrame.
    return pd.read_csv(filename)


def categorize_review_length(length: int) -> str:
    """Return review length category."""
    # Категории длины выбраны вручную:
    # short  — короткий отзыв,
    # medium — средний отзыв,
    # long   — длинный отзыв.
    if length < 500:
        return "short"

    if length < 1500:
        return "medium"

    return "long"


def analyze_dataset(dataframe: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    """Analyze IMDB reviews dataset and build report."""
    # copy() нужен, чтобы не изменять исходный DataFrame напрямую.
    df = dataframe.copy()

    # Проверяем, что в датасете есть нужные столбцы.
    # review — текст отзыва.
    # sentiment — тональность отзыва: positive или negative.
    required_columns = {"review", "sentiment"}

    if not required_columns.issubset(df.columns):
        raise ValueError("В датасете должны быть столбцы 'review' и 'sentiment'.")

    # Series — это одномерная структура данных Pandas.
    # Здесь создается Series review_length:
    # для каждого отзыва считается длина текста в символах.
    review_length = df["review"].str.len()

    # Добавляем Series в DataFrame как новый столбец.
    df["review_length"] = review_length

    # Lambda-функция применяется к каждому значению столбца review_length.
    # В результате создается новый столбец length_category.
    df["length_category"] = df["review_length"].apply(
        lambda length: categorize_review_length(length)
    )

    # value_counts() считает, сколько раз встречается каждое значение.
    sentiment_counts = df["sentiment"].value_counts()
    category_counts = df["length_category"].value_counts()

    # groupby группирует строки по sentiment,
    # затем mean считает среднюю длину отзывов в каждой группе.
    average_length_by_sentiment = df.groupby("sentiment")["review_length"].mean()

    # Разница средних длин между positive и negative.
    # Это нужно для вывода: отличаются ли отзывы по средней длине.
    if {"positive", "negative"}.issubset(average_length_by_sentiment.index):
        positive_mean = average_length_by_sentiment["positive"]
        negative_mean = average_length_by_sentiment["negative"]
        mean_difference = abs(positive_mean - negative_mean)
    else:
        mean_difference = 0

    # .loc обращается к строкам/столбцам по меткам.
    loc_example = df.loc[0, ["sentiment", "review_length", "length_category"]]

    # .iloc обращается к строкам/столбцам по числовым позициям.
    iloc_example = df.iloc[0][["sentiment", "review_length", "length_category"]]

    # Чтобы отчет не был огромным, выводим только компактные столбцы.
    compact_head = df[["sentiment", "review_length", "length_category"]].head()

    report_lines = [
        "Задание 6. Анализ датасета IMDB с помощью Pandas",
        "Разработчик: Kruchonok Aleksandra Sergeevna",
        "Дата разработки: 2026-04-21",
        "=" * 70,
        "",
        f"Размер датасета: {df.shape[0]} строк, {df.shape[1]} столбцов",
        f"Столбцы датасета: {list(df.columns)}",
        "",
        "Первые 5 строк после обработки:",
        str(compact_head),
        "",
        "Пример Series review_length:",
        str(df["review_length"].head()),
        "",
        "Пример .loc для первой строки:",
        str(loc_example),
        "",
        "Пример .iloc для первой строки:",
        str(iloc_example),
        "",
        "Количество отзывов по тональности:",
        str(sentiment_counts),
        "",
        "Количество отзывов по категориям длины:",
        str(category_counts),
        "",
        "Средняя длина отзыва по тональности:",
        str(average_length_by_sentiment),
        "",
        f"Разница средних длин positive и negative: {mean_difference:.2f} символов",
        "",
        "Вывод:",
    ]

    if mean_difference < 100:
        report_lines.append(
            "Средние длины положительных и отрицательных отзывов близки. "
            "Значит, одна только длина текста не является надежным признаком "
            "для определения тональности отзыва."
        )
    else:
        report_lines.append(
            "Средние длины положительных и отрицательных отзывов заметно отличаются. "
            "Это значит, что длина текста может быть дополнительным признаком, "
            "но по одной длине нельзя точно определить тональность."
        )

    return df, "\n".join(report_lines)


def save_report(report: str) -> None:
    """Save report to text file."""
    # Создаем папку output, если ее еще нет.
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # write_text записывает текст в файл.
    # Если файл уже существует, он будет перезаписан.
    RESULT_FILE.write_text(report, encoding="utf-8")


def run_task_6() -> None:
    """Run task 6."""
    while True:
        print("\nЗадание 6. Анализ IMDB Dataset с помощью Pandas.")
        print("Разработчик: Kruchonok Aleksandra Sergeevna")
        print("Дата разработки: 2026-04-21")

        try:
            dataframe = load_dataset(DATA_FILE)
            analyzed_dataframe, report = analyze_dataset(dataframe)

            print("\n" + report)

            save_report(report)

            print(f"\nОтчет сохранен в файл: {RESULT_FILE}")

            print("\nПервые 10 обработанных строк:")
            print(
                analyzed_dataframe[
                    ["sentiment", "review_length", "length_category"]
                ].head(10)
            )

        except FileNotFoundError as error:
            print(error)
            print("\nКак исправить:")
            print("1. Скачай датасет с Kaggle.")
            print("2. Распакуй архив.")
            print("3. Положи только файл 'IMDB Dataset.csv' в папку data.")

        except Exception as error:
            print(f"Ошибка при обработке датасета: {error}")

        if not ask_yes_no("\nRepeat task 6? (y/n): "):
            break