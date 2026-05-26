"""Laboratory Work No. 4.

Task 3. ln(1 + x), class, statistics and matplotlib plot.

Variant 13:
ln(1 + x) = x - x^2 / 2 + x^3 / 3 - ...

Version: 1.3
Developer: Kruchonok Aleksandra Sergeevna
Development date: 2026-04-14
"""

from __future__ import annotations

import math
import statistics
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt

from utils.input_utils import ask_int_in_range, ask_positive_float, ask_yes_no


OUTPUT_DIR = Path("output")
PLOT_FILE = OUTPUT_DIR / "task3_ln_series_plot.png"


class LnSeriesExperiment:
    """Calculate ln(1 + x) using a power series and analyze results."""

    MAX_ITERATIONS = 20000

    def __init__(self, eps: float) -> None:
        """Initialize experiment with selected precision."""
        # self — ссылка на текущий объект; eps хранится внутри объекта и используется всеми методами класса.
        self.eps = eps

        # Данные таблицы хранятся в отдельных списках.
        self.table_x: list[float] = []
        self.table_terms: list[int] = []
        self.table_series_values: list[float] = []
        self.table_math_values: list[float] = []

    @staticmethod
    def is_valid_x(x: float) -> bool:
        """Check if x belongs to the convergence interval."""
        # Ряд ln(1 + x) сходится при -1 < x <= 1.
        # безопасный интервал -0.8 ... 0.8.
        return -1 < x < 1

    def calculate_series(self, x: float) -> tuple[float, int]:
        """Calculate ln(1 + x) using the power series."""
        if not self.is_valid_x(x):
            raise ValueError("x must satisfy -1 < x < 1.")

        # Формула ряда: ln(1 + x) = x - x^2/2 + x^3/3 - x^4/4 + ...
        result = 0.0
        term = x
        n = 1

        # Суммируем члены ряда, пока модуль текущего члена >= eps.
        while abs(term) >= self.eps and n <= self.MAX_ITERATIONS:
            result += term

            # Рекуррентная формула для следующего члена ряда.
            # Если текущий член: (-1)^(n-1) * x^n / n, то следующий получаем умножением на -x*n/(n+1).
            n += 1
            term *= -x * (n - 1) / n

        terms_count = n - 1
        return result, terms_count

    @staticmethod
    def make_x_values(start: float, end: float, count: int) -> list[float]:
        """Create evenly spaced x values."""
        step = (end - start) / (count - 1)
        return [start + step * index for index in range(count)]

    def build_table_points(self, start: float, end: float, count: int) -> None:
        """Build table values."""
        self.table_x.clear()
        self.table_terms.clear()
        self.table_series_values.clear()
        self.table_math_values.clear()

        x_values = self.make_x_values(start, end, count)

        for x in x_values:
            series_value, terms_count = self.calculate_series(x)
            math_value = math.log(1 + x)

            self.table_x.append(x)
            self.table_terms.append(terms_count)
            self.table_series_values.append(series_value)
            self.table_math_values.append(math_value)

    def calculate_statistics(self) -> dict[str, float]:
        """Calculate mean, median, mode, variance and standard deviation."""
        values = self.table_series_values

        if not values:
            return {
                "mean": 0.0,
                "median": 0.0,
                "mode": 0.0,
                "variance": 0.0,
                "standard_deviation": 0.0,
            }

        # Среднее арифметическое — сумма значений / количество значений.
        mean_value = statistics.mean(values)

        # Медиана — центральное значение отсортированной последовательности.
        # Если элементов четное количество, берется среднее двух центральных.
        median_value = statistics.median(values)

        # Мода — самое часто встречающееся значение.
        # Для float-значений почти все числа разные, округление до 4 знаков.
        rounded_values = [round(value, 4) for value in values]
        mode_counter = Counter(rounded_values)
        mode_value = mode_counter.most_common(1)[0][0]

        # Дисперсия — среднее арифметическое квадратов отклонений от среднего.
        variance_value = statistics.pvariance(values)

        # СКО — стандартное квадратическое отклонение, квадратный корень из дисперсии.
        standard_deviation_value = statistics.pstdev(values)

        return {
            "mean": mean_value,
            "median": median_value,
            "mode": mode_value,
            "variance": variance_value,
            "standard_deviation": standard_deviation_value,
        }

    def print_table(self) -> None:
        """Print calculation table."""
        print("\n" + "-" * 95)
        print(
            f"{'x':>12} "
            f"{'n':>8} "
            f"{'Series F(x)':>20} "
            f"{'math.log(1+x)':>20} "
            f"{'Difference':>15}"
        )
        print("-" * 95)

        for x, n, series_value, math_value in zip(
            self.table_x,
            self.table_terms,
            self.table_series_values,
            self.table_math_values,
        ):
            difference = abs(series_value - math_value)

            print(
                f"{x:>12.6f} "
                f"{n:>8} "
                f"{series_value:>20.10f} "
                f"{math_value:>20.10f} "
                f"{difference:>15.2e}"
            )

        print("-" * 95)

    @staticmethod
    def draw_math_axes(
        ax,
        x_min: float,
        x_max: float,
        y_min: float,
        y_max: float,
    ) -> None:
        """Draw mathematical coordinate axes with arrows."""
        # Убираем рамку matplotlib.
        ax.spines[["left", "right", "top", "bottom"]].set_visible(False)

        # Ось Ox — горизонтальная стрелка.
        ax.annotate(
            "",
            xy=(x_max, 0),
            xytext=(x_min, 0),
            arrowprops={"arrowstyle": "->", "linewidth": 1.2, "color": "black"},
        )

        # Ось Oy — вертикальная стрелка.
        ax.annotate(
            "",
            xy=(0, y_max),
            xytext=(0, y_min),
            arrowprops={"arrowstyle": "->", "linewidth": 1.2, "color": "black"},
        )

        # Подпись Ox ставим справа после конца стрелки.
        ax.text(
            x_max,
            -0.04 * (y_max - y_min),
            "Ox",
            fontsize=12,
            ha="left",
            va="top",
            clip_on=False,
        )

        # Подпись Oy ставим сверху после конца стрелки.
        ax.text(
            0.03 * (x_max - x_min),
            y_max,
            "Oy",
            fontsize=12,
            ha="left",
            va="bottom",
            clip_on=False,
        )

    def build_plot(self, filename: Path) -> None:
        """Build and save the plot."""
        filename.parent.mkdir(parents=True, exist_ok=True)

        # Для таблицы пользователь выбирает немного точек.
        # Для графика берем много точек, чтобы кривая была плавной, а не прямой.
        plot_x = self.make_x_values(-0.8, 0.8, 200)

        plot_series_values = [self.calculate_series(x)[0] for x in plot_x]
        plot_math_values = [math.log(1 + x) for x in plot_x]

        all_y_values = plot_series_values + plot_math_values

        x_min = min(plot_x) - 0.1
        x_max = max(plot_x) + 0.1
        y_min = min(all_y_values) - 0.2
        y_max = max(all_y_values) + 0.2

        fig, ax = plt.subplots(figsize=(10, 6))

        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)

        # Первый график — значения, рассчитанные через ряд.
        ax.plot(
            plot_x,
            plot_series_values,
            linewidth=2,
            label="Power series F(x)",
        )

        # Второй график — значения через math.log.
        # linestyle="--" задает пунктирный стиль линии.
        ax.plot(
            plot_x,
            plot_math_values,
            linewidth=2,
            linestyle="--",
            label="math.log(1 + x)",
        )

        # Рисуем математические оси Ox и Oy со стрелками.
        self.draw_math_axes(ax, x_min, x_max, y_min, y_max)

        # Сетка помогает визуально читать значения.
        ax.grid(True)

        # Заголовок поднят выше через pad.
        ax.set_title("Graph of ln(1 + x)", fontsize=15, pad=28)

        # Легенда формируется из label в ax.plot(). bbox_to_anchor переносит легенду вниз под график.
        ax.legend(
            loc="upper center",
            bbox_to_anchor=(0.5, -0.12),
            ncol=2,
        )

        # Оставляем место снизу под легенду и сверху под заголовок.
        fig.subplots_adjust(bottom=0.22, top=0.82)

        # Сохранение графика в файл.
        # dpi=300 задает хорошее качество изображения. bbox_inches="tight" обрезает лишние поля.
        plt.savefig(filename, dpi=300, bbox_inches="tight")

        # Показываем график на экране.
        plt.show()


def run_task_3() -> None:
    """Run task 3."""
    while True:
        print("\nTask 3. ln(1 + x), statistics and matplotlib.")
        print("Developer: Kruchonok Aleksandra Sergeevna")
        print("Development date: 2026-04-14")

        print("\nFor the series ln(1 + x), use interval -1 < x < 1.")
        eps = ask_positive_float("Enter eps, for example 0.0001: ")

        print("\nThe program uses a safe interval from -0.8 to 0.8.")
        count = ask_int_in_range("Enter number of table points from 3 to 30: ", 3, 30)

        experiment = LnSeriesExperiment(eps=eps)

        # type показывает тип объекта.
        print(f"\nObject type: {type(experiment)}")

        experiment.build_table_points(start=-0.8, end=0.8, count=count)

        experiment.print_table()

        statistics_result = experiment.calculate_statistics()

        print("\nAdditional statistical parameters for F(x):")
        print(f"Mean: {statistics_result['mean']:.10f}")
        print(f"Median: {statistics_result['median']:.10f}")
        print(f"Mode rounded to 4 decimals: {statistics_result['mode']:.4f}")
        print(f"Variance: {statistics_result['variance']:.10f}")
        print(f"Standard deviation: {statistics_result['standard_deviation']:.10f}")

        experiment.build_plot(PLOT_FILE)
        print(f"\nPlot saved to: {PLOT_FILE}")

        if not ask_yes_no("\nRepeat task 3? (y/n): "):
            break