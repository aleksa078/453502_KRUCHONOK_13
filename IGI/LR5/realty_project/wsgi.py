"""WSGI-конфигурация для production (Gunicorn, Render и т.д.)."""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realty_project.settings')

application = get_wsgi_application()
