"""Ожидание готовности БД для Docker Compose/production."""
import time

from django.core.management.base import BaseCommand
from django.db import OperationalError, connections


class Command(BaseCommand):
    """Команда ждёт, пока default database начнёт принимать подключения."""

    help = 'Wait until database is available.'

    def add_arguments(self, parser):
        """Добавляет параметры попыток и задержки."""
        parser.add_argument('--retries', type=int, default=30)
        parser.add_argument('--delay', type=float, default=1.0)

    def handle(self, *args, **options):
        """Проверяет подключение к БД с повторными попытками."""
        retries = options['retries']
        delay = options['delay']
        for attempt in range(1, retries + 1):
            try:
                connections['default'].ensure_connection()
                self.stdout.write(self.style.SUCCESS('Database is available.'))
                return
            except OperationalError as exc:
                self.stdout.write(f'Database unavailable ({attempt}/{retries}): {exc}')
                time.sleep(delay)
        raise OperationalError('Database is not available after retries.')
