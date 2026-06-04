"""Контекст-процессор для вывода таймзоны, текущей даты и текстового календаря."""
from django.utils import timezone

from core.timezone_utils import format_dd_mm_yyyy, get_user_timezone_name, text_calendar


def timezone_context(request):
    """Добавляет переменные user_timezone, now_user, now_utc и calendar_text во все шаблоны."""
    tz_name = get_user_timezone_name(request)
    now = timezone.now()
    now_local = timezone.localtime(now)
    return {
        'user_timezone': tz_name,
        'now_user': now_local,
        'now_user_formatted': format_dd_mm_yyyy(now_local),
        'now_utc': now,
        'now_utc_formatted': now.strftime('%d/%m/%Y %H:%M'),
        'calendar_text': text_calendar(now_local.year, now_local.month, tz_name),
    }
