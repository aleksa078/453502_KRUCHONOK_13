import os
import circle
import square

# Считываем данные из переменных окружения Docker.
# Если они не переданы, берем значения по умолчанию (например, 3.0)
radius = float(os.environ.get('RADIUS', 3.0))
side = float(os.environ.get('SIDE', 3.0))

print("=== Геометрический Калькулятор в Docker ===")
print(f"Данные на входе: Радиус = {radius}, Сторона квадрата = {side}\n")

print("КРУГ:")
print(f" - Площадь: {circle.area(radius):.2f}")
print(f" - Периметр: {circle.perimeter(radius):.2f}\n")

print("КВАДРАТ:")
print(f" - Площадь: {square.area(side)}")
print(f" - Периметр: {square.perimeter(side)}")

# Он обращается к библиотеке os (операционная система).
# Лезет в словарь environ (тот самый справочник со стикерами).
# Ищет стикер с именем RADIUS.
# Находит там 15.5 и забирает его для расчетов

# -e RADIUS=15.5
# Если бы мы не передали флаг -e, скрипт бы не нашел стикер и взял бы 
# запасное значение 3.0, которое мы указали вторым аргументом в скобках