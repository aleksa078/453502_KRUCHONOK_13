"""Тесты представлений и доступа."""
import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from core.models import NewsArticle, UserProfile


@pytest.mark.django_db
def test_home_page(client):
    NewsArticle.objects.create(
        title='T', summary='S', full_text='F', is_published=True
    )
    r = client.get(reverse('home'))
    assert r.status_code == 200
    assert b'news' in r.content.lower() or 'T'.encode() in r.content


@pytest.mark.django_db
def test_privacy_page(client):
    assert client.get(reverse('privacy')).status_code == 200


@pytest.mark.django_db
def test_catalog_search(client):
    r = client.get(reverse('catalog'), {'q': 'test'})
    assert r.status_code == 200


@pytest.mark.django_db
def test_api_requires_auth(client):
    r = client.get(reverse('api_sales'))
    assert r.status_code in (401, 302)


@pytest.mark.django_db
def test_statistics_forbidden_for_guest(client):
    r = client.get(reverse('statistics'))
    assert r.status_code in (302, 403)


@pytest.mark.django_db
def test_statistics_for_employee(client):
    u = User.objects.create_user('emp1', password='x')
    UserProfile.objects.update_or_create(
        user=u,
        defaults={
            'role': 'employee',
            'birth_date': '1990-01-01',
            'phone': '+375 (29) 111-11-11',
            'timezone': 'Europe/Minsk',
        },
    )
    from core.models import Employee
    Employee.objects.create(
        user=u, full_name='E', email='e@e.by',
        phone='+375 (29) 111-11-11', birth_date='1990-01-01', hire_date='2020-01-01',
    )
    client.login(username='emp1', password='x')
    assert client.get(reverse('statistics')).status_code == 200
