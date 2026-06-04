"""Регрессионные тесты для исправлений ЛР5."""
from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils import timezone

from core.forms import RegisterForm
from core.models import Buyer, Category, Employee, Property, Sale, UserProfile


@pytest.mark.django_db
def test_public_registration_form_has_no_employee_role():
    """Публичная форма регистрации не должна давать выбрать роль сотрудника."""
    form = RegisterForm()
    assert 'role' not in form.fields


@pytest.mark.django_db
def test_property_negative_price_is_invalid():
    """Модельная валидация запрещает отрицательную цену."""
    category = Category.objects.create(name='Квартиры')
    prop = Property(
        title='Тест',
        price=Decimal('-1'),
        description='Описание',
        characteristics='40 м²',
        category=category,
    )
    with pytest.raises(ValidationError):
        prop.full_clean()


@pytest.mark.django_db
def test_api_sales_returns_401_for_anonymous(client):
    """API сделок не редиректит анонима, а отдаёт JSON 401."""
    response = client.get(reverse('api_sales'))
    assert response.status_code == 401
    assert response.json()['error'] == 'auth required'


@pytest.mark.django_db
def test_client_can_purchase_property(client):
    """Клиент может купить активный объект через frontend-кнопку."""
    category = Category.objects.create(name='Дома')
    prop = Property.objects.create(
        title='Дом',
        price=Decimal('100000'),
        description='Описание дома',
        characteristics='100 м²',
        category=category,
    )
    emp_user = User.objects.create_user('employee', 'e@example.com', 'pass12345')
    UserProfile.objects.update_or_create(
        user=emp_user,
        defaults={
            'role': UserProfile.ROLE_EMPLOYEE,
            'birth_date': date(1990, 1, 1),
            'phone': '+375 (29) 111-11-11',
            'timezone': 'Europe/Minsk',
        },
    )
    employee = Employee.objects.create(
        user=emp_user,
        full_name='Сотрудник',
        department='Продажи',
        phone='+375 (29) 111-11-11',
        email='e@example.com',
        birth_date=date(1990, 1, 1),
        hire_date=date(2020, 1, 1),
    )
    prop.agents.add(employee)

    user = User.objects.create_user('client1', 'c@example.com', 'pass12345')
    UserProfile.objects.update_or_create(
        user=user,
        defaults={
            'role': UserProfile.ROLE_CLIENT,
            'birth_date': date(1995, 1, 1),
            'phone': '+375 (33) 222-22-22',
            'timezone': 'Europe/Minsk',
        },
    )
    Buyer.objects.create(
        user=user,
        full_name='Клиент',
        email='c@example.com',
        phone='+375 (33) 222-22-22',
        birth_date=date(1995, 1, 1),
    )

    client.force_login(user)
    response = client.post(reverse('property_buy', args=[prop.pk]), {'confirm': 'on'})
    assert response.status_code == 302
    assert Sale.objects.filter(property=prop, buyer=user.buyer).exists()
    prop.refresh_from_db()
    assert prop.is_active is False


@pytest.mark.django_db
def test_timestamp_saves_local_text(client):
    """При сохранении объекта сохраняется текст локального времени и имя таймзоны."""
    timezone.activate('Europe/Minsk')
    category = Category.objects.create(name='Новостройки')
    prop = Property.objects.create(
        title='Квартира',
        price=Decimal('120000'),
        description='Описание квартиры',
        characteristics='60 м²',
        category=category,
    )
    assert prop.created_at_local_text
    assert prop.created_at_timezone in ('Europe/Minsk', 'Europe/Moscow', 'Europe/Kyiv', 'UTC') or 'Europe/' in prop.created_at_timezone


@pytest.mark.django_db
def test_public_registration_view_creates_client_profile_and_buyer(client):
    """Регистрация через сайт не падает из-за signal и создаёт только клиента."""
    response = client.post(reverse('register'), {
        'username': 'new_client',
        'email': 'new_client@example.com',
        'birth_date': '1995-01-01',
        'phone': '+375 (29) 123-45-67',
        'timezone': 'Europe/Minsk',
        'password1': 'StrongPass12345!',
        'password2': 'StrongPass12345!',
    })
    assert response.status_code == 302
    user = User.objects.get(username='new_client')
    assert user.profile.role == UserProfile.ROLE_CLIENT
    assert Buyer.objects.filter(user=user).exists()


@pytest.mark.django_db
def test_seed_data_leaves_active_properties_for_client_purchase():
    """После seed_data часть объектов продана для статистики, а часть доступна для покупки."""
    call_command('seed_data', '--with-demo-users')
    assert Property.objects.count() == 10
    assert Sale.objects.count() == 5
    assert Property.objects.filter(is_active=True, sales__isnull=True).distinct().count() == 5
