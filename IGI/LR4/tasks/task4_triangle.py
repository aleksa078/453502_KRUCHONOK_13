"""Laboratory Work No. 4.

Task 4. Triangle class hierarchy.

Variant 13:
Build a triangle with sides a, b, c.

Version: 2.3
Developer: Kruchonok Aleksandra Sergeevna
Development date: 2026-04-17
"""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from pathlib import Path

import matplotlib.pyplot as plt

from utils.input_utils import ask_non_empty_string, ask_positive_float, ask_yes_no


OUTPUT_DIR = Path("output")
TRIANGLE_IMAGE = OUTPUT_DIR / "task4_triangle.png"
TRIANGLE_INFO = OUTPUT_DIR / "task4_triangle_info.txt"


class GeometricFigure(ABC):
    """Abstract base class for geometric figures."""

    # Атрибут класса, принадлежит классу.
    figure_type = "Geometric figure"

    def __init__(self, name: str) -> None:
        """Initialize a geometric figure."""
        # self — ссылка на текущий объект.
        # name — динамический атрибут объекта, создается во время __init__.
        self.name = name

    @abstractmethod
    def calculate_area(self) -> float:
        """Calculate figure area."""

    @classmethod
    def get_figure_type(cls) -> str:
        """Return figure type."""
        # cls — ссылка на класс.
        # вызывается через имя класса: Triangle.get_figure_type().
        return cls.figure_type

    @staticmethod
    def is_positive(value: float) -> bool:
        """Check whether value is positive."""
        # Статический метод не использует ни self, ни cls. Он просто логически относится к классу.
        return value > 0


class FigureColor:
    """Store and validate a figure color."""

    ALLOWED_COLORS = {
        "red",
        "green",
        "blue",
        "yellow",
        "orange",
        "purple",
        "black",
        "white",
        "pink",
        "gray",
        "cyan",
    }

    def __init__(self, color: str) -> None:
        """Initialize color storage."""
        # __color — private-атрибут.
        # Снаружи напрямую к нему обращаться не нужно.
        self.__color = "blue"

        # Через property-сеттер сразу проверяем корректность цвета.
        self.color = color

    @property
    def color(self) -> str:
        """Get figure color."""
        # Getter возвращает значение private-атрибута.
        return self.__color

    @color.setter
    def color(self, value: str) -> None:
        """Set figure color."""
        # Setter проверяет значение перед записью.
        normalized = value.strip().lower()

        if not normalized:
            raise ValueError("Color cannot be empty.")

        if normalized not in self.ALLOWED_COLORS:
            raise ValueError(
                f"Unsupported color: {value}. "
                f"Use one of: {', '.join(sorted(self.ALLOWED_COLORS))}."
            )

        self.__color = normalized


class PerimeterMixin:
    """Mixin that adds perimeter functionality."""

    def calculate_perimeter(self) -> float:
        """Calculate figure perimeter."""
        # Mixin использует _sides. protected-атрибут, у класса Triangle.
        return sum(self._sides)

    def perimeter_text(self) -> str:
        """Return formatted perimeter text."""
        return f"Perimeter: {self.calculate_perimeter():.4f}"


class Triangle(PerimeterMixin, GeometricFigure):
    """Represent a triangle with sides a, b and c."""

    # Переопределяем атрибут класса базового класса.
    figure_type = "Triangle"

    def __init__(self, a: float, b: float, c: float, color: str, text: str) -> None:
        """Initialize a triangle."""
        # super() вызывает __init__ родительского класса GeometricFigure, базовая часть объекта получает имя "Triangle".
        super().__init__(name="Triangle")

        if not self.is_valid_sides(a, b, c):
            raise ValueError("Triangle sides are invalid.")

        # Одно подчеркивание — protected.
        # атрибут  для внутреннего использования и для использования в наследниках.
        self._sides = [a, b, c]

        # Два  подчеркивания — private через name mangling.
        # Python переименует __label примерно в _Triangle__label.
        self.__label = text

        # Композиция: внутри Triangle хранится объект FigureColor.
        # Triangle не наследуется от FigureColor, а использует его.
        self._figure_color = FigureColor(color)

    @staticmethod
    def is_valid_sides(a: float, b: float, c: float) -> bool:
        """Check triangle inequality."""
        return (
            a > 0
            and b > 0
            and c > 0
            and a + b > c
            and a + c > b
            and b + c > a
        )

    @property
    def a(self) -> float:
        """Get first side."""
        return self._sides[0]

    @property
    def b(self) -> float:
        """Get second side."""
        return self._sides[1]

    @property
    def c(self) -> float:
        """Get third side."""
        return self._sides[2]

    @property
    def color(self) -> str:
        """Get triangle color."""
        return self._figure_color.color

    @color.setter
    def color(self, value: str) -> None:
        """Set triangle color."""
        self._figure_color.color = value

    @property
    def label(self) -> str:
        """Get triangle label."""
        return self.__label

    @label.setter
    def label(self, value: str) -> None:
        """Set triangle label."""
        normalized = value.strip()

        if not normalized:
            raise ValueError("Label cannot be empty.")

        self.__label = normalized

    def calculate_area(self) -> float:
        """Calculate triangle area using Heron's formula."""
        # Формула Герона:
        # p = (a + b + c) / 2
        # S = sqrt(p * (p-a) * (p-b) * (p-c))
        semi_perimeter = self.calculate_perimeter() / 2

        return math.sqrt(
            semi_perimeter
            * (semi_perimeter - self.a)
            * (semi_perimeter - self.b)
            * (semi_perimeter - self.c)
        )

    def get_coordinates(self) -> tuple[list[float], list[float]]:
        """Calculate triangle coordinates for drawing."""
        # Размещаем сторону c на оси Ox:
        # A = (0, 0), B = (c, 0).
        # Координаты C считаем из длин сторон.
        x_c = (self.b ** 2 + self.c ** 2 - self.a ** 2) / (2 * self.c)
        y_c = math.sqrt(max(self.b ** 2 - x_c ** 2, 0))

        # Последняя точка повторяет первую, чтобы линия замкнулась.
        x_values = [0, self.c, x_c, 0]
        y_values = [0, 0, y_c, 0]

        return x_values, y_values

    def get_info(self) -> str:
        """Return formatted triangle information."""
        return (
            f"{self.name}\n"
            f"a = {self.a:.2f}\n"
            f"b = {self.b:.2f}\n"
            f"c = {self.c:.2f}\n"
            f"color = {self.color}\n"
            f"area = {self.calculate_area():.4f}\n"
            f"{self.perimeter_text()}"
        )

    @staticmethod
    def draw_math_axes(
        ax,
        x_min: float,
        x_max: float,
        y_min: float,
        y_max: float,
    ) -> None:
        """Draw mathematical coordinate axes with arrows."""
        # Убираем стандартную рамку matplotlib.
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

        # Подпись Ox справа после конца стрелки.
        ax.text(
            x_max,
            -0.05 * (y_max - y_min),
            "Ox",
            fontsize=12,
            ha="left",
            va="top",
            clip_on=False,
        )

        # Подпись Oy сверху после конца стрелки.
        ax.text(
            0.03 * (x_max - x_min),
            y_max,
            "Oy",
            fontsize=12,
            ha="left",
            va="bottom",
            clip_on=False,
        )

    def draw(self, image_path: Path, info_path: Path) -> None:
        """Draw triangle and save it to files."""
        image_path.parent.mkdir(parents=True, exist_ok=True)

        x_values, y_values = self.get_coordinates()

        max_x = max(x_values)
        max_y = max(y_values)

        # Оставляем справа место для подписи в рамке.
        x_min = -0.5
        x_max = max_x + 3.2
        y_min = -0.5
        y_max = max_y + 0.8

        fig, ax = plt.subplots(figsize=(9, 6))

        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)

        # Заливка треугольника.
        ax.fill(
            x_values,
            y_values,
            color=self.color,
            alpha=0.35,
            label="Triangle area",
        )

        # Контур треугольника.
        ax.plot(
            x_values,
            y_values,
            marker="o",
            linewidth=2,
            label="Triangle border",
        )

        # Математические оси Ox/Oy.
        self.draw_math_axes(ax, x_min, x_max, y_min, y_max)

        # Подпись фигуры в рамке справа от фигурки
        ax.text(
            max_x + 0.35,
            max_y * 0.55 if max_y else 0.5,
            f"{self.label}\n\n{self.get_info()}",
            fontsize=10,
            ha="left",
            va="center",
            bbox={
                "boxstyle": "round",
                "facecolor": "white",
                "edgecolor": "black",
                "alpha": 0.9,
            },
        )

        # Заголовок графика.
        ax.set_title("Triangle with sides a, b, c", fontsize=15, pad=28)

        # Сетка.
        ax.grid(True)

        # Сохраняем одинаковый масштаб по осям, чтобы фигура не искажалась.
        ax.set_aspect("equal", adjustable="box")

        # Легенда формируется из label в ax.fill и ax.plot.
        ax.legend(
            loc="upper center",
            bbox_to_anchor=(0.5, -0.10),
            ncol=2,
        )

        # Оставляем место под легенду и заголовок.
        fig.subplots_adjust(bottom=0.20, top=0.82)

        # Сохранение картинки.
        plt.savefig(image_path, dpi=300, bbox_inches="tight")
        plt.show()

        # Сохранение текстовой информации о фигуре.
        info_path.write_text(self.get_info(), encoding="utf-8")

    def __str__(self) -> str:
        """Return readable string representation."""
        # print(triangle) вызывает именно __str__.
        return self.get_info()

    def __repr__(self) -> str:
        """Return technical string representation."""
        return (
            f"Triangle(a={self.a!r}, b={self.b!r}, "
            f"c={self.c!r}, color={self.color!r}, label={self.label!r})"
        )

    def __len__(self) -> int:
        """Return number of triangle sides."""
        # Позволяет вызвать len(triangle).
        return 3

    def __getitem__(self, index: int) -> float:
        """Get side by index."""
        # Позволяет обращаться к сторонам по индексу:
        # triangle[0], triangle[1], triangle[2].
        return self._sides[index]

    def __eq__(self, other: object) -> bool:
        """Compare triangles by area."""
        # Переопределение оператора ==.
        if not isinstance(other, Triangle):
            return NotImplemented

        return math.isclose(self.calculate_area(), other.calculate_area())

    def __lt__(self, other: "Triangle") -> bool:
        """Compare triangles by area."""
        # Переопределение оператора <.
        return self.calculate_area() < other.calculate_area()


def ask_color() -> str:
    """Read correct matplotlib color."""
    while True:
        color = ask_non_empty_string(
            "Enter color in English "
            "(red/green/blue/yellow/orange/purple/black/white/pink/gray/cyan): "
        )

        try:
            FigureColor(color)
            return color
        except ValueError as error:
            print(error)


def run_task_4() -> None:
    """Run task 4."""
    while True:
        print("\nTask 4. Triangle class hierarchy.")
        print("Developer: Kruchonok Aleksandra Sergeevna")
        print("Development date: 2026-04-17")

        while True:
            a = ask_positive_float("Enter side a: ")
            b = ask_positive_float("Enter side b: ")
            c = ask_positive_float("Enter side c: ")

            if Triangle.is_valid_sides(a, b, c):
                break

            print("Input error: these sides cannot form a triangle.")

        color = ask_color()
        label = ask_non_empty_string("Enter triangle label text: ")

        triangle = Triangle(a=a, b=b, c=c, color=color, text=label)

        print("\nTriangle created:")
        print(triangle)

        print("\nClass and object examples:")
        print(f"type(triangle): {type(triangle)}")
        print(f"Class method Triangle.get_figure_type(): {Triangle.get_figure_type()}")
        print(f"Static method Triangle.is_valid_sides(a, b, c): {Triangle.is_valid_sides(a, b, c)}")

        print("\nMagic methods examples:")
        print(f"str(triangle): {str(triangle)}")
        print(f"repr(triangle): {repr(triangle)}")
        print(f"len(triangle): {len(triangle)}")
        print(f"triangle[0]: {triangle[0]}")
        print(f"triangle[1]: {triangle[1]}")
        print(f"triangle[2]: {triangle[2]}")

        print("\nEncapsulation examples:")
        print(f"Protected field triangle._sides: {triangle._sides}")
        print(f"Private label through property triangle.label: {triangle.label}")
        print("Private technical access: triangle._Triangle__label")

        triangle.draw(TRIANGLE_IMAGE, TRIANGLE_INFO)

        print(f"\nTriangle image saved to: {TRIANGLE_IMAGE}")
        print(f"Triangle information saved to: {TRIANGLE_INFO}")

        if not ask_yes_no("\nRepeat task 4? (y/n): "):
            break