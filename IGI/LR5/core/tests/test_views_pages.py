import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from core.models import Category, Property, UserProfile


@pytest.mark.django_db
def test_all_static_pages(client):
    for name in ['about', 'news', 'faq', 'contacts', 'vacancies', 'reviews', 'promos', 'register']:
        assert client.get(reverse(name)).status_code == 200


@pytest.mark.django_db
def test_property_crud_flow(client):
    cat = Category.objects.create(name='Cat1')
    u = User.objects.create_user('emp2', password='pass')
    UserProfile.objects.update_or_create(
        user=u,
        defaults={
            'role': 'employee',
            'birth_date': '1990-01-01',
            'phone': '+375 (29) 111-11-12',
            'timezone': 'Europe/Minsk',
        },
    )
    from core.models import Employee
    Employee.objects.create(
        user=u, full_name='E2', email='e2@e.by',
        phone='+375 (29) 111-11-12', birth_date='1990-01-01', hire_date='2020-01-01',
    )
    client.login(username='emp2', password='pass')
    r = client.post(reverse('property_create'), {
        'title': 'New Flat',
        'price': '100000',
        'description': 'd',
        'characteristics': 'c',
        'category': cat.pk,
        'is_active': True,
    })
    assert r.status_code == 302
    prop = Property.objects.get(title='New Flat')
    assert client.get(reverse('property_detail', args=[prop.pk])).status_code == 200
