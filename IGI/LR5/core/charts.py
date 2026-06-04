"""Диаграммы средствами Python matplotlib, без JavaScript."""
import logging
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from django.conf import settings
from django.db.models import Sum
from django.utils.text import slugify

logger = logging.getLogger('core')


def _charts_dir():
    """Создаёт и возвращает каталог media/charts."""
    path = Path(settings.MEDIA_ROOT) / 'charts'
    path.mkdir(parents=True, exist_ok=True)
    return path


def _safe_suffix(suffix):
    """Делает безопасный суффикс имени файла графика."""
    return slugify(str(suffix or 'all')) or 'all'


def chart_sales_by_category(sales_queryset=None, suffix='all'):
    """Создаёт PNG-диаграмму суммы продаж по категориям и возвращает URL."""
    from core.models import Sale

    qs = sales_queryset if sales_queryset is not None else Sale.objects.all()
    rows = qs.values('property__category__name').annotate(total=Sum('amount')).order_by('-total')
    labels = [r['property__category__name'] or 'Без категории' for r in rows]
    values = [float(r['total'] or 0) for r in rows]
    if not labels:
        labels, values = ['Нет данных'], [0]

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(labels, values)
    ax.set_title('Сумма сделок по категориям')
    ax.set_ylabel('BYN')
    plt.xticks(rotation=25, ha='right')
    plt.tight_layout()
    filename = f'sales_by_category_{_safe_suffix(suffix)}.png'
    out = _charts_dir() / filename
    fig.savefig(out, dpi=100)
    plt.close(fig)
    return f'{settings.MEDIA_URL}charts/{filename}'


def chart_sales_timeline(sales_queryset=None, suffix='all'):
    """Создаёт PNG-график количества продаж по месяцам и возвращает URL."""
    from core.models import Sale

    qs = sales_queryset if sales_queryset is not None else Sale.objects.all()
    dates = list(qs.values_list('sale_date', flat=True))
    if not dates:
        months, counts = ['—'], [0]
    else:
        keys = [d.strftime('%Y-%m') for d in dates if d]
        counter = Counter(keys)
        months = sorted(counter.keys())
        counts = [counter[m] for m in months]

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(months, counts, marker='o')
    ax.set_title('Динамика продаж по месяцам')
    ax.set_ylabel('Кол-во сделок')
    plt.xticks(rotation=30, ha='right')
    plt.tight_layout()
    filename = f'sales_timeline_{_safe_suffix(suffix)}.png'
    out = _charts_dir() / filename
    fig.savefig(out, dpi=100)
    plt.close(fig)
    return f'{settings.MEDIA_URL}charts/{filename}'
