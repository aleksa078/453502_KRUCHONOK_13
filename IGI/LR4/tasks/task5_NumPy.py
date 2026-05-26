""" Laboratory Work No. 4.
Task 5. NumPy arrays, matrix initialization, indexing, slices, universal functions, mathematical and statistical operations.

Variant 13:
Create a new matrix by dividing all elements of the source matrix by the maximum absolute element. 
Calculate variance of the new matrix using NumPy and manually by formula.

Version: 1.1
Developer: Kruchonok Aleksandra Sergeevna
Development date: 2026-04-19
"""

from __future__ import annotations

import numpy as np

from utils.input_utils import ask_int_in_range, ask_yes_no


def create_random_matrix(rows: int, columns: int) -> np.ndarray:
    """Create a random integer matrix.

    Args:
        rows: Number of rows.
        columns: Number of columns.

    Returns:
        NumPy integer matrix.
    """
    # np.random.default_rng()  генератор  чисел NumPy, чтобы получить случайные значения для матрицы.
    rng = np.random.default_rng()

    # rng.integers() создает NumPy-массив случайных целых чисел.
    # low=-50 — минимальное значение включительно.  high=51 — верхняя граница не включается, значит максимум будет 50.
    # size=(rows, columns) задает размер матрицы.
    # Возвращается ndarray — основной тип массива в NumPy.
    return rng.integers(low=-50, high=51, size=(rows, columns))


def normalize_by_max_abs(matrix: np.ndarray) -> np.ndarray:
    """Divide all matrix elements by the maximum absolute element.

    Args:
        matrix: Source matrix.

    Returns:
        Normalized matrix.

    Raises:
        ValueError: If maximum absolute value is zero.
    """
    # np.abs(matrix) применяет модуль к каждому элементу матрицы.
    # Например, -12 станет 12.
    # np.max(...) находит максимальный элемент.
    # максимальный элемент именно по модулю.
    max_abs_value = np.max(np.abs(matrix))

    # Если вся матрица состоит из нулей, max(abs(A)) будет равен 0.
    # Делить на 0 нельзя, ошибку.
    if max_abs_value == 0:
        raise ValueError("Cannot divide by zero maximum absolute value.")

    # NumPy поддерживает векторизованные операции:
    # matrix / max_abs_value делит сразу каждый элемент матрицы на одно число.
    return matrix / max_abs_value


def calculate_variance_manually(matrix: np.ndarray) -> float:
    """Calculate variance manually by formula.

    Args:
        matrix: Source matrix.

    Returns:
        Variance value.
    """
    # matrix.ravel() превращает двумерную матрицу в одномерный массив.
    # Например:
    # [[1, 2],
    #  [3, 4]]
    # станет [1, 2, 3, 4].
    # Так удобно считать статистику по всем элементам.
    flat_values = matrix.ravel()

    # np.mean() считает среднее арифметическое:
    # сумма всех элементов / количество элементов.
    mean_value = np.mean(flat_values)

    # Для дисперсии нужно найти отклонение каждого элемента от среднего,
    # затем возвести эти отклонения в квадрат.
    # NumPy делает это сразу для всего массива.
    squared_differences = (flat_values - mean_value) ** 2

    # np.sum() считает сумму квадратов отклонений.
    # flat_values.size — количество элементов.
    # Формула дисперсии:
    # D = sum((x_i - mean)^2) / n
    # делим на n, поэтому считаем генеральную дисперсию.
    return float(np.sum(squared_differences) / flat_values.size)


def calculate_mode_manually(matrix: np.ndarray) -> float:
    """Calculate mode using NumPy methods."""
    # Мода — это самое часто встречающееся значение.
    # В NumPy нет простой функции np.mode.
    # Поэтому используем np.unique(..., return_counts=True).
    # unique_values — массив уникальных значений.
    # counts — сколько раз каждое значение встретилось.
    unique_values, counts = np.unique(matrix, return_counts=True)

    # np.argmax(counts) возвращает индекс самого большого количества повторений.
    mode_index = np.argmax(counts)

    # По этому индексу берем значение, которое встречается чаще всего.
    return float(unique_values[mode_index])


def demonstrate_numpy_initialization() -> None:
    """Demonstrate basic NumPy array initialization methods."""
    print("\nNumPy initialization examples:")

    # np.array() создает NumPy-массив из обычного Python-списка.
    # Отличие NumPy array от list:
    # list может хранить элементы разных типов: [1, "text", 3.5].
    # NumPy array обычно хранит элементы одного типа.
    # За счет этого массивы NumPy быстрее и компактнее для вычислений.
    example_array = np.array([1, 2, 3, 4])
    print(f"np.array([1, 2, 3, 4]): {example_array}")

    # np.zeros() создает матрицу заданного размера, заполненную нулями.
    zeros_matrix = np.zeros((2, 3))
    print(f"np.zeros((2, 3)):\n{zeros_matrix}")

    # np.ones() создает матрицу заданного размера, заполненную единицами.
    ones_matrix = np.ones((2, 3))
    print(f"np.ones((2, 3)):\n{ones_matrix}")

    # np.empty() создает массив заданного размера, но не заполняет его конкретными значениями.
    # Там могут быть старые случайные значения из памяти.
    empty_matrix = np.empty((2, 2))
    print(f"np.empty((2, 2)):\n{empty_matrix}")

    # np.full() создает матрицу заданного размера
    # и заполняет все элементы указанным значением.
    full_matrix = np.full((2, 3), 7)
    print(f"np.full((2, 3), 7):\n{full_matrix}")

    # np.eye() создает единичную матрицу:
    # на главной диагонали стоят 1, все остальные элементы равны 0.
    identity_matrix = np.eye(3)
    print(f"np.eye(3):\n{identity_matrix}")

    # np.arange() создает одномерный массив чисел с шагом.
    # Здесь числа от 1 до 10 с шагом 2: 1, 3, 5, 7, 9.
    arange_array = np.arange(1, 10, 2)
    print(f"np.arange(1, 10, 2): {arange_array}")


def demonstrate_indexing_and_slicing(matrix: np.ndarray) -> None:
    """Demonstrate indexing and slicing.

    Args:
        matrix: Source matrix.
    """
    print("\nIndexing and slicing examples:")

    # matrix[0, 0] — элемент первой строки и первого столбца. В Python индексация начинается с 0.
    print(f"First element matrix[0, 0]: {matrix[0, 0]}")

    # matrix[0, :] — первая строка целиком.
    # 0 означает первую строку, : означает "все столбцы".
    print(f"First row matrix[0, :]: {matrix[0, :]}")

    # matrix[:, 0] — первый столбец целиком.
    # : означает "все строки", 0 означает первый столбец.
    print(f"First column matrix[:, 0]: {matrix[:, 0]}")

    # matrix[:2, :2] — срез:
    # первые две строки и первые два столбца.
    print(f"Slice matrix[:2, :2]:\n{matrix[:2, :2]}")


def run_task_5() -> None:
    """Run task 5."""
    while True:
        print("\nTask 5. NumPy matrix processing.")
        print("Developer: Kruchonok Aleksandra Sergeevna")
        print("Development date: 2026-04-19")

        rows = ask_int_in_range("Enter number of rows from 2 to 10: ", 2, 10)
        columns = ask_int_in_range("Enter number of columns from 2 to 10: ", 2, 10)

        # Создаем исходную случайную целочисленную матрицу A.
        matrix = create_random_matrix(rows, columns)

        # Создаем новую матрицу B по условию варианта:
        # B = A / max(abs(A)).
        normalized_matrix = normalize_by_max_abs(matrix)

        # np.var() считает дисперсию средствами NumPy.
        # По умолчанию np.var делит на n, то есть считает генеральную дисперсию.
        variance_numpy = float(np.var(normalized_matrix))

        # Считаем ту же дисперсию вручную по формуле.
        variance_manual = calculate_variance_manually(normalized_matrix)

        # Мода — самое часто встречающееся значение.
        # Считаем ее через np.unique и np.argmax.
        mode_value = calculate_mode_manually(normalized_matrix)

        print("\nSource integer matrix A:")
        print(matrix)

        # Демонстрация разных способов создания массивов NumPy.
        demonstrate_numpy_initialization()

        # Демонстрация индексации и срезов.
        demonstrate_indexing_and_slicing(matrix)

        print("\nUniversal function examples:")

        # np.abs(A) — универсальная функция.
        # Она применяется к каждому элементу массива.
        print(f"np.abs(A):\n{np.abs(matrix)}")

        # np.max(np.abs(A)) — максимальный по модулю элемент.
        print(f"np.max(np.abs(A)): {np.max(np.abs(matrix))}")

        # Векторизованные операции NumPy:
        # A + 10 прибавляет 10 ко всем элементам матрицы.
        # A * 2 умножает все элементы матрицы на 2.
        print(f"A + 10:\n{matrix + 10}")
        print(f"A * 2:\n{matrix * 2}")

        print("\nNew matrix B = A / max(abs(A)):")
        print(normalized_matrix)

        print("\nStatistical functions:")

        # np.mean(B) — среднее арифметическое:
        # сумма всех элементов / количество элементов.
        print(f"np.mean(B): {np.mean(normalized_matrix):.4f}")

        # np.median(B) — медиана.
        # Медиана — центральное значение отсортированного набора.
        # Если количество элементов четное, берется среднее двух центральных.
        print(f"np.median(B): {np.median(normalized_matrix):.4f}")

        # Мода — самое повторяющееся значение.
        # В коде получена через np.unique(..., return_counts=True).
        print(f"Mode by np.unique: {mode_value:.4f}")

        # np.std(B) — стандартное квадратическое отклонение.
        # Это квадратный корень из дисперсии.
        print(f"np.std(B): {np.std(normalized_matrix):.4f}")

        # np.var(B) — дисперсия:
        # среднее значение квадратов отклонений от среднего.
        print(f"np.var(B): {variance_numpy:.4f}")

        print("\nVariance comparison:")
        print(f"Variance by np.var: {round(variance_numpy, 2)}")
        print(f"Variance by manual formula: {round(variance_manual, 2)}")

        # np.isclose() сравнивает вещественные числа с учетом небольшой погрешности.
        # Для float-чисел лучше использовать isclose, а не ==.
        if np.isclose(variance_numpy, variance_manual):
            print("The results match.")
        else:
            print("The results are different because of calculation precision.")

        if not ask_yes_no("\nRepeat task 5? (y/n): "):
            break