#!/usr/bin/env python
"""Точка входа Django: запуск dev-сервера и management-команд."""
import os
import sys


def main():
    """Запускает administrative-задачи Django."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realty_project.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Install dependencies from requirements.txt."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
