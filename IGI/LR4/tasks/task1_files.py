"""Laboratory Work No. 4.

Task 1. CSV and pickle serialization.

Variant 13:
Exported goods summary:
product name, importing country, shipment amount in pieces.

Version: 1.2
Developer: Kruchonok Aleksandra Sergeevna
Development date: 2026-04-11
"""

# Исходные данные - словарь. поместить их в файл (сериализаторы pickle и CSV). 
# Организовать считывание данных, поиск, сортировку.
# Сводка об экспортируемых товарах: 
# наименование товара, 
# страна, импортирующая товар, 
# объем партии в штуках. 
# Напечатать списки стран и общий объем его экспорта. 
# Вывести инфу о товаре, введенном с клавиатуры


from __future__ import annotations

import csv
import pickle
import zipfile
from dataclasses import dataclass
from pathlib import Path

from utils.input_utils import ask_non_empty_string, ask_yes_no


OUTPUT_DIR = Path("output")

CSV_FILE = OUTPUT_DIR / "task1_export_goods.csv"
PICKLE_FILE = OUTPUT_DIR / "task1_export_goods.pkl"
ARCHIVE_FILE = OUTPUT_DIR / "task1_export_goods_archive.zip"

CSV_FIELDS = ["product", "country", "amount"] 

# Если архивирование не нужно, False.
CREATE_ARCHIVE = True

@dataclass
class ExportRecord:
    """Store one export record."""

    product: str
    country: str
    amount: int

    # метод экземпляра
    def to_dict(self) -> dict[str, str | int]:
        """Convert the object to a dictionary."""
        return {
            "product": self.product,
            "country": self.country,
            "amount": self.amount,
        }

    # метод класса
    @classmethod
    def from_dict(cls, row: dict[str, str]) -> "ExportRecord":
        """Create an object from a dictionary."""
        return cls(
            product=row["product"],
            country=row["country"],
            amount=int(row["amount"]), # из CSV все значения читаются как строки
        )


class ExportCatalog:
    """Store records and perform search, sorting and calculations."""

    # инициализатор объекта (заполняет объект данными после создания)
    def __init__(self, records: list[ExportRecord]) -> None:
        """Initialize the catalog."""
        self.records = records

    # Поиск (сравнивает введенный товар с названием каждого товара)
    def find(self, product_name: str) -> list[ExportRecord]:
        """Find records by product name."""
        product_name = product_name.strip().lower() # lower - не зависеть от регистра

        return [
            record
            for record in self.records
            if record.product.lower() == product_name
        ]

    # Список стран и общий объем
    def countries_and_total(self, product_name: str) -> tuple[list[str], int]:
        """Return importing countries and total export amount."""
        found_records = self.find(product_name)
        countries = sorted({record.country for record in found_records})
        total = sum(record.amount for record in found_records)

        return countries, total

    # сортировка по названию товара, потом по стране, по объему 
    def sorted_records(self) -> list[ExportRecord]:
        """Return records sorted by product, country and amount."""
        return sorted(
            self.records,
            key=lambda record: (
                record.product.lower(),
                record.country.lower(),
                record.amount,
            ),
        )


def create_catalog() -> ExportCatalog:
    """Create source data."""
    source_data = {
        "wheat": [("Poland", 1200), ("Germany", 850), ("Italy", 730)],
        "potatoes": [("Lithuania", 600), ("Latvia", 410), ("Poland", 900)],
        "tractors": [("Kazakhstan", 35), ("Armenia", 17), ("Georgia", 21)],
        "linen": [("France", 320), ("Germany", 280), ("Spain", 175)],
        "cheese": [("Poland", 500), ("Lithuania", 240), ("Czech Republic", 310)],
    }

    records = []

    for product, deliveries in source_data.items():
        for country, amount in deliveries:
            records.append(ExportRecord(product, country, amount))

    return ExportCatalog(records)


def save_to_csv(catalog: ExportCatalog) -> None:
    """Save records to a CSV file."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # w автоматически перезаписывает файл, если он уже существует
    with CSV_FILE.open("w", encoding="utf-8", newline="") as file:
        # запись словаря в CSV (1 метод CSV)
        writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)
        # запись в CSV первой строки - заголовков столбцов таблицы (3 метод CSV)
        writer.writeheader()

        for record in catalog.records:
            # запись в CSV словаря построчно (4 метод CSV)
            writer.writerow(record.to_dict())

# считывание
def load_from_csv() -> ExportCatalog:
    """Load records from a CSV file."""
    records = []

    with CSV_FILE.open("r", encoding="utf-8", newline="") as file:
        # читает CSV-файл построчно и предсталяет каждую строку как словарь (2 метод CSV)
        reader = csv.DictReader(file)

        for row in reader:
            records.append(ExportRecord.from_dict(row))

    return ExportCatalog(records)


def save_to_pickle(catalog: ExportCatalog) -> None:
    """Save records using pickle serializer."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    #Сериализация (pickle dump)
    # Режим "wb" автоматически перезаписывает бинарный файл.
    with PICKLE_FILE.open("wb") as file:
        pickle.dump(catalog.records, file)
 
# считывание
def load_from_pickle() -> ExportCatalog:
    """Load records from a pickle file."""

    #Десериализация (pickle load) 
    with PICKLE_FILE.open("rb") as file:
        records = pickle.load(file)

    return ExportCatalog(records)


# архивирование
def create_archive() -> None:
    """Create ZIP archive and print compression percent."""
    # mode="w" автоматически перезаписывает архив, если он уже существует.
    with zipfile.ZipFile(
        ARCHIVE_FILE,
        mode="w", # запись в архив
        compression=zipfile.ZIP_DEFLATED, # алгоритм сжатия
        compresslevel=9, # макс степень сжатия
    ) as archive:
        archive.write(CSV_FILE, arcname=CSV_FILE.name)
        archive.write(PICKLE_FILE, arcname=PICKLE_FILE.name)

    print("\nArchive information:")

    # чтение из архива
    with zipfile.ZipFile(ARCHIVE_FILE, mode="r") as archive:
        for file_info in archive.infolist():
            original_size = file_info.file_size
            compressed_size = file_info.compress_size

            if original_size == 0:
                compression_percent = 0
            else:
                 # расчет % сжатия
                compression_percent = (1 - compressed_size / original_size) * 100

            print("-" * 60)
            print(f"File in archive: {file_info.filename}")
            print(f"Original size: {original_size} bytes")
            print(f"Compressed size: {compressed_size} bytes")
            print(f"Compression percent: {compression_percent:.2f}%")

        # получаем инфу о файлах без распаковки
        csv_info = archive.getinfo(CSV_FILE.name)
        print("-" * 60)
        print("Information received by getinfo() without extracting the file:")
        print(f"{csv_info.filename}: {csv_info.file_size} bytes")


def print_records(records: list[ExportRecord]) -> None:
    """Print records as a table."""
    print("\n" + "-" * 65)
    print(f"{'Product':<18} {'Country':<25} {'Amount':>10}")
    print("-" * 65)

    for record in records:
        print(f"{record.product:<18} {record.country:<25} {record.amount:>10}")

    print("-" * 65)


def process_search(catalog: ExportCatalog) -> None:
    """Search product information entered by the user."""
    product_name = ask_non_empty_string("\nEnter product name: ")
    found_records = catalog.find(product_name)

    if not found_records:
        print("No records found for this product.")
        return

    countries, total = catalog.countries_and_total(product_name)

    print_records(found_records)
    print(f"Countries importing '{product_name}': {', '.join(countries)}")
    print(f"Total export amount: {total} pieces")


def run_task_1() -> None:
    """Run task 1."""
    while True:
        print("\nTask 1. Exported goods, CSV and pickle.")
        print("Developer: Kruchonok Aleksandra Sergeevna")
        print("Development date: 2026-04-11")

        catalog = create_catalog()

        save_to_csv(catalog)
        save_to_pickle(catalog)

        # CSV считывается корректно.
        csv_catalog = load_from_csv()

        # Pickle тоже считывается, но второй раз таблицу не выводим.
        pickle_catalog = load_from_pickle()

        print("\nData loaded from CSV and sorted (Pickle - same, test in code):")
        print_records(csv_catalog.sorted_records())

        print(f"\nRecords loaded from pickle: {len(pickle_catalog.records)}")

        process_search(csv_catalog)

        if CREATE_ARCHIVE:
            create_archive()
            print(f"\nArchive file: {ARCHIVE_FILE}")

        print(f"\nCSV file: {CSV_FILE}")
        print(f"Pickle file: {PICKLE_FILE}")

        if not ask_yes_no("\nRepeat task 1? (y/n): "):
            break