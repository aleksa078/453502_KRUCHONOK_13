"""Параллельный код: ThreadPoolExecutor для одновременных внешних API-запросов."""
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from core.external_api import fetch_age_by_name, fetch_cat_fact, fetch_weather

logger = logging.getLogger('core')


def fetch_home_widgets_parallel(city, user_name):
    """Параллельно загружает OpenWeather, Agify и Cat Facts для главной страницы."""
    tasks = {
        'weather': lambda: fetch_weather(city),
        'cat_fact': fetch_cat_fact,
        'agify': lambda: fetch_age_by_name(user_name or 'alex'),
    }
    results = {}
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(fn): key for key, fn in tasks.items()}
        for future in as_completed(futures):
            key = futures[future]
            try:
                results[key] = future.result()
            except Exception as exc:
                logger.error('Parallel fetch %s failed: %s', key, exc)
                results[key] = {'error': str(exc)}
    return results
