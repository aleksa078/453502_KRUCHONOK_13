"""Внешние API с кэшированием, чтобы главная страница не тормозила на каждом запросе."""
import logging

import requests
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger('core')


def _cached(key, loader):
    """Возвращает значение из кэша или загружает его через loader()."""
    cached = cache.get(key)
    if cached is not None:
        return cached
    result = loader()
    cache.set(key, result, settings.EXTERNAL_API_CACHE_SECONDS)
    return result


def fetch_weather(city=None):
    """Получает погоду OpenWeather по названию города, а не по таймзоне."""
    city = (city or settings.DEFAULT_CITY_WEATHER).strip() or settings.DEFAULT_CITY_WEATHER
    cache_key = f'weather:{city.lower()}'

    def load():
        api_key = settings.OPENWEATHER_API_KEY
        if not api_key:
            return {
                'city': city,
                'description': 'Демо: добавьте OPENWEATHER_API_KEY в .env/Render Environment',
                'temp': '—',
            }
        try:
            resp = requests.get(
                'https://api.openweathermap.org/data/2.5/weather',
                params={'q': city, 'appid': api_key, 'units': 'metric', 'lang': 'ru'},
                timeout=4,
            )
            resp.raise_for_status()
            data = resp.json()
            return {
                'city': data['name'],
                'temp': round(data['main']['temp'], 1),
                'description': data['weather'][0]['description'],
            }
        except requests.RequestException as exc:
            logger.warning('OpenWeather error: %s', exc)
            return {'city': city, 'temp': '—', 'description': 'API недоступен', 'error': str(exc)}

    return _cached(cache_key, load)


def _fallback_age_by_name(name):
    """
    Возвращает локальный fallback для Agify.

    Это не замена внешнего API, а защита от временной ошибки 429 Too Many Requests.
    Основной код всё равно сначала пытается обратиться к Agify.io.
    """
    normalized = (name or 'guest').strip().lower() or 'guest'

    demo_ages = {
        'guest': 64,
        'alex': 49,
        'алексей': 42,
        'anna': 31,
        'анна': 31,
        'maria': 29,
        'мария': 29,
        'sasha': 26,
        'саша': 26,
    }

    age = demo_ages.get(normalized)

    if age is None:
        age = 25 + (sum(ord(ch) for ch in normalized) % 35)

    return {
        'name': name or 'guest',
        'age': age,
        'count': 0,
        'source': 'fallback',
        'message': 'Agify временно недоступен или достигнут лимит запросов; показано локальное fallback-значение.',
    }

def fetch_age_by_name(name):
    """
    Agify.io — внешний API для определения предполагаемого возраста по имени.

    Защита для Render:
    - результат кэшируется, чтобы не делать запрос при каждом открытии страницы;
    - 429 Too Many Requests не ломает сайт;
    - если Agify временно недоступен, возвращается fallback-значение.
    """
    name = (name or 'guest').strip() or 'guest'
    cache_key = f'external_api:agify:{name.lower()}'

    cached = cache.get(cache_key)
    if cached:
        return cached

    try:
        response = requests.get(
            'https://api.agify.io/',
            params={'name': name},
            timeout=5,
        )

        if response.status_code == 429:
            result = _fallback_age_by_name(name)
            result['error'] = 'Agify.io вернул 429 Too Many Requests.'
            cache.set(cache_key, result, 60 * 60 * 12)
            logger.info('Agify rate limit for name=%s; fallback value returned', name)
            return result

        response.raise_for_status()
        data = response.json()

        result = {
            'name': data.get('name') or name,
            'age': data.get('age') or _fallback_age_by_name(name)['age'],
            'count': data.get('count') or 0,
            'source': 'agify',
        }

        cache.set(cache_key, result, 60 * 60 * 6)
        return result

    except requests.RequestException as exc:
        result = _fallback_age_by_name(name)
        result['error'] = f'Agify временно недоступен: {exc}'
        cache.set(cache_key, result, 60 * 30)
        logger.info('Agify unavailable for name=%s; fallback value returned: %s', name, exc)
        return result


def fetch_cat_fact():
    """Получает факт о кошках через Cat Facts API."""
    def load():
        try:
            resp = requests.get('https://catfact.ninja/fact', timeout=4)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as exc:
            logger.warning('CatFact error: %s', exc)
            return {'fact': 'API недоступен', 'error': str(exc)}

    return _cached('cat_fact:daily', load)
