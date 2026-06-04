"""
Настройки проекта «Риэлтерское агентство» (вариант 13).

Ключевые требования ЛР5:
- локально используется SQLite, в production/Docker/Render — PostgreSQL;
- пользовательская таймзона не захардкожена: она берётся из профиля, сессии
  или HTTP-заголовка X-Timezone, затем активируется middleware;
- серверная TIME_ZONE остаётся UTC, потому что aware-datetime в БД Django
  хранит в UTC при USE_TZ=True;
- дата/время для пользователя выводятся через django.utils.timezone.localtime().
"""
import os
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() == 'true'

if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = 'django-insecure-lr5-dev-key-change-only-for-local-debug'
    else:
        raise RuntimeError('DJANGO_SECRET_KEY must be set when DJANGO_DEBUG=False')

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
    if host.strip()
]

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get('DJANGO_CSRF_TRUSTED_ORIGINS', '').split(',')
    if origin.strip()
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core.apps.CoreConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'core.middleware.UserTimezoneMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'realty_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.timezone_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'realty_project.wsgi.application'

DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    # Render/Railway/Fly часто передают подключение одной строкой DATABASE_URL.
    DATABASES = {
        'default': dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            ssl_require=not DEBUG,
        )
    }
elif os.environ.get('POSTGRES_DB'):
    # Локальный docker-compose.
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('POSTGRES_DB', 'realty_db'),
            'USER': os.environ.get('POSTGRES_USER', 'realty_user'),
            'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'realty_pass'),
            'HOST': os.environ.get('POSTGRES_HOST', 'db'),
            'PORT': os.environ.get('POSTGRES_PORT', '5432'),
        }
    }
else:
    # Локальный запуск без Docker.
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
# Учебный проект должен показывать загруженные изображения на Render без внешнего S3/Cloudinary.
# Для production-систем лучше хранить media во внешнем объектном хранилище.
SERVE_MEDIA_FILES = os.environ.get('DJANGO_SERVE_MEDIA_FILES', 'True').lower() == 'true'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'home'

LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': LOG_DIR / 'realty.log',
            'formatter': 'verbose',
        },
    },
    'root': {'handlers': ['console', 'file'], 'level': LOG_LEVEL},
    'loggers': {'core': {'level': LOG_LEVEL, 'propagate': True}},
}

# Внешние API.
OPENWEATHER_API_KEY = os.environ.get('OPENWEATHER_API_KEY', '')
DEFAULT_CITY_WEATHER = os.environ.get('DEFAULT_CITY_WEATHER', 'Minsk')
DEFAULT_USER_TIMEZONE = os.environ.get('DEFAULT_USER_TIMEZONE', 'Europe/Minsk')
API_REQUIRE_AUTH = True

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'lr5-realty-cache',
    }
}
EXTERNAL_API_CACHE_SECONDS = int(os.environ.get('EXTERNAL_API_CACHE_SECONDS', '300'))

os.environ.setdefault('MPLBACKEND', 'Agg')

if not DEBUG:
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'True').lower() == 'true'
    CSRF_COOKIE_SECURE = os.environ.get('CSRF_COOKIE_SECURE', 'True').lower() == 'true'
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'False').lower() == 'true'
