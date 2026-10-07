"""Тесты таймзоны."""
from django.utils import timezone

from core.timezone_utils import activate_user_timezone, format_dd_mm_yyyy, get_user_timezone_name


def test_format_date():
    assert format_dd_mm_yyyy(None) == '—'


def test_activate_timezone():
    tz = activate_user_timezone('Europe/Minsk')
    now = timezone.now()
    assert now.tzinfo is not None


def test_get_timezone_anonymous(rf):
    req = rf.get('/')
    req.user = type('U', (), {'is_authenticated': False})()
    req.session = {}
    assert get_user_timezone_name(req) == 'Europe/Minsk'
