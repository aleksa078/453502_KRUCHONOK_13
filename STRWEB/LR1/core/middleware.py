"""
Middleware пользовательской таймзоны.

Зона не захардкожена: берётся через get_user_timezone_name(). При ошибке в строке
таймзоны используется fallback из settings.DEFAULT_USER_TIMEZONE.
"""
import logging

from core.timezone_utils import activate_user_timezone, get_user_timezone_name

logger = logging.getLogger('core')


class UserTimezoneMiddleware:
    """Активирует IANA-таймзону пользователя на время обработки запроса."""

    def __init__(self, get_response):
        """Сохраняет callable следующего middleware/view."""
        self.get_response = get_response

    def __call__(self, request):
        """Определяет, активирует и кладёт таймзону в request.user_timezone."""
        tz_name = get_user_timezone_name(request)
        request.user_timezone = tz_name
        activate_user_timezone(tz_name)
        logger.debug('Activated timezone %s for %s', tz_name, request.path)
        return self.get_response(request)
