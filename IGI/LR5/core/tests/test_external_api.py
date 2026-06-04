from unittest.mock import patch

from core.external_api import fetch_age_by_name, fetch_cat_fact, fetch_weather


@patch('core.external_api.requests.get')
def test_fetch_weather_no_key(mock_get):
    from django.conf import settings
    settings.OPENWEATHER_API_KEY = ''
    r = fetch_weather('Minsk')
    assert 'city' in r
    mock_get.assert_not_called()


@patch('core.external_api.requests.get')
def test_fetch_age(mock_get):
    mock_get.return_value.json.return_value = {'name': 'ivan', 'age': 30}
    mock_get.return_value.raise_for_status = lambda: None
    assert fetch_age_by_name('ivan')['age'] == 30


@patch('core.external_api.requests.get')
def test_fetch_cat(mock_get):
    mock_get.return_value.json.return_value = {'fact': 'cats'}
    mock_get.return_value.raise_for_status = lambda: None
    assert 'fact' in fetch_cat_fact()
