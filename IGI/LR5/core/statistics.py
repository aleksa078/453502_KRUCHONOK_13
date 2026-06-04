"""Статистика по предметной области: продажи, клиенты, категории.

Здесь считаются показатели для страницы /statistics/.
Важно для защиты:
- возраст клиентов не хранится отдельным числом и не имитируется;
- возраст рассчитывается по полю Buyer.birth_date;
- статистика продаж считается по реальным записям Sale;
- графики строятся отдельно в core/charts.py средствами Python matplotlib, без JavaScript.
"""

from statistics import mean, median, multimode

from django.utils import timezone


def calculate_age(birth_date, today=None):
    """
    Рассчитывает полный возраст по дате рождения.

    Используется для статистики по клиентам.
    Возраст не хранится в базе как отдельное поле, потому что он меняется со временем.
    Поэтому правильнее каждый раз вычислять его по Buyer.birth_date.

    Пример:
    birth_date = 2000-06-10
    today = 2026-06-04
    возраст = 25, потому что день рождения в 2026 году ещё не наступил.
    """
    if not birth_date:
        return None

    today = today or timezone.localdate()

    return (
        today.year
        - birth_date.year
        - ((today.month, today.day) < (birth_date.month, birth_date.day))
    )


def sale_amount_stats(queryset):
    """
    Возвращает среднее, медиану, моду, сумму и количество сделок.

    queryset — это QuerySet модели Sale.
    Для расчётов используется поле Sale.amount.
    """
    if hasattr(queryset, 'values_list'):
        amounts = list(queryset.values_list('amount', flat=True))
    else:
        amounts = [getattr(item, 'amount', 0) for item in queryset]

    if not amounts:
        return {
            'mean': 0,
            'median': 0,
            'mode': 0,
            'total': 0,
            'count': 0,
        }

    values = [float(amount or 0) for amount in amounts]
    modes = multimode(values)

    return {
        'mean': round(mean(values), 2),
        'median': round(median(values), 2),
        'mode': round(modes[0], 2) if modes else 0,
        'total': round(sum(values), 2),
        'count': len(values),
    }


def client_age_stats(buyers):
    """
    Возвращает средний и медианный возраст клиентов.

    Важно:
    - раньше здесь ошибочно использовалось b.age;
    - у Buyer нет поля age;
    - возраст корректно считается из Buyer.birth_date.
    """
    ages = []

    for buyer in buyers:
        birth_date = getattr(buyer, 'birth_date', None)
        age = calculate_age(birth_date)

        if age is not None:
            ages.append(age)

    if not ages:
        return {
            'mean': 0,
            'median': 0,
            'count': 0,
        }

    return {
        'mean': round(mean(ages), 1),
        'median': round(median(ages), 1),
        'count': len(ages),
    }


def popular_category_by_count(properties_queryset=None):
    """
    Определяет самую популярную категорию по количеству объектов недвижимости.

    Для superuser считаются все объекты.
    Для сотрудника во views.py передаётся только QuerySet его объектов.
    """
    from django.db.models import Count

    from core.models import Property

    qs = properties_queryset if properties_queryset is not None else Property.objects.all()

    row = (
        qs.values('category__name')
        .annotate(cnt=Count('id'))
        .order_by('-cnt', 'category__name')
        .first()
    )

    return row or {
        'category__name': '—',
        'cnt': 0,
    }


def profitable_category(sales_queryset=None):
    """
    Определяет категорию недвижимости, которая принесла наибольшую сумму продаж.

    Используется поле Sale.amount.
    Группировка идёт по Property.category.
    """
    from django.db.models import Sum

    from core.models import Sale

    qs = sales_queryset if sales_queryset is not None else Sale.objects.all()

    row = (
        qs.values('property__category__name')
        .annotate(total=Sum('amount'))
        .order_by('-total', 'property__category__name')
        .first()
    )

    return row or {
        'property__category__name': '—',
        'total': 0,
    }