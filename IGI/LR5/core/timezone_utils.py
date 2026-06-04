"""
Утилиты таймзоны через стандартную библиотеку zoneinfo и django.utils.timezone.

Как это объяснять преподавателю:
1. В settings.py TIME_ZONE='UTC' — серверная зона для хранения aware datetime.
2. Пользовательская зона не захардкожена: берётся из UserProfile.timezone,
   затем из request.session['user_timezone'], затем из X-Timezone header,
   затем из settings.DEFAULT_USER_TIMEZONE.
3. ZoneInfo проверяет, что строка — настоящая IANA-таймзона.
4. timezone.activate(tz) активирует выбранную зону на время запроса.
5. timezone.now() даёт текущий aware-момент; для показа пользователю используется
   timezone.localtime(timezone.now()).
"""
import calendar
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError, available_timezones

from django.conf import settings
from django.utils import timezone as dj_timezone


def valid_timezone_choices(limit_to_europe=True):
    """Возвращает список IANA-таймзон для формы профиля/регистрации."""
    zones = sorted(available_timezones())
    if limit_to_europe:
        zones = [z for z in zones if z.startswith('Europe/') or z == 'UTC']
    return [(z, z) for z in zones]


def valid_timezone_name(tz_name):
    """Проверяет, что строка является настоящей IANA-таймзоной."""
    try:
        ZoneInfo(tz_name)
        return True
    except (ZoneInfoNotFoundError, ValueError, TypeError):
        return False


def safe_zoneinfo(tz_name):
    """Безопасно преобразует строку таймзоны в ZoneInfo с fallback."""
    default_name = getattr(settings, 'DEFAULT_USER_TIMEZONE', 'Europe/Minsk')
    return ZoneInfo(tz_name if valid_timezone_name(tz_name) else default_name)


def get_user_timezone_name(request):
    """
    Определяет таймзону пользователя без хардкода в view/templates.

    Приоритет:
    1) request.user.profile.timezone;
    2) request.session['user_timezone'];
    3) HTTP header X-Timezone / HTTP_X_TIMEZONE;
    4) settings.DEFAULT_USER_TIMEZONE.
    """
    default_name = getattr(settings, 'DEFAULT_USER_TIMEZONE', 'Europe/Minsk')

    if getattr(request, 'user', None) and request.user.is_authenticated:
        profile = getattr(request.user, 'profile', None)
        if profile and getattr(profile, 'timezone', None):
            tz_name = profile.timezone
            if valid_timezone_name(tz_name):
                return tz_name

    session_tz = request.session.get('user_timezone')
    if session_tz and valid_timezone_name(session_tz):
        return session_tz

    header_tz = request.headers.get('X-Timezone') or request.META.get('HTTP_X_TIMEZONE')
    if header_tz and valid_timezone_name(header_tz):
        return header_tz

    return default_name


def activate_user_timezone(tz_name):
    """Активирует пользовательскую таймзону для текущего request/thread."""
    tz = safe_zoneinfo(tz_name)
    dj_timezone.activate(tz)
    return tz


def now_utc():
    """Возвращает текущий aware datetime; при USE_TZ=True хранится в UTC."""
    return dj_timezone.now()


def current_timezone_name():
    """Возвращает имя активной таймзоны Django."""
    return getattr(dj_timezone.get_current_timezone(), 'key', str(dj_timezone.get_current_timezone()))


def to_user_local(dt, tz_name=None):
    """Конвертирует datetime в локальное время пользователя/активной зоны."""
    if dt is None:
        return None
    if dj_timezone.is_naive(dt):
        dt = dj_timezone.make_aware(dt, ZoneInfo('UTC'))
    tz = safe_zoneinfo(tz_name) if tz_name else dj_timezone.get_current_timezone()
    return dt.astimezone(tz)


def local_stamp_text(dt=None, tz_name=None):
    """Сохраняемая строка локального времени: DD/MM/YYYY HH:MM:SS TZ."""
    local_dt = to_user_local(dt or dj_timezone.now(), tz_name)
    return local_dt.strftime('%d/%m/%Y %H:%M:%S %Z')


def format_dd_mm_yyyy(dt):
    """Формат даты DD/MM/YYYY для отображения."""
    if dt is None:
        return '—'
    if isinstance(dt, datetime):
        return to_user_local(dt).strftime('%d/%m/%Y %H:%M')
    return dt.strftime('%d/%m/%Y')


def text_calendar(year, month, tz_name):
    """Возвращает текстовый календарь месяца средствами Python, без JavaScript."""
    cal = calendar.TextCalendar(firstweekday=0)
    header = f'Календарь {month:02d}/{year} (таймзона: {tz_name})\n'
    return header + cal.formatmonth(year, month)
