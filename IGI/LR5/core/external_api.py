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


def fetch_age_by_name(name):
    """Получает предполагаемый возраст по имени через Agify.io."""
    name = (name or 'alex').strip() or 'alex'
    cache_key = f'agify:{name.lower()}'

    def load():
        try:
            resp = requests.get('https://api.agify.io/', params={'name': name}, timeout=4)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as exc:
            logger.warning('Agify error: %s', exc)
            return {'name': name, 'age': None, 'error': str(exc)}

    return _cached(cache_key, load)


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
