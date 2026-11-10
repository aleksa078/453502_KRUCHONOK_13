"""Регрессионные тесты галереи недвижимости, новостей homeFULL и CRUD-сценариев."""
from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone

from core.forms import PropertyForm
from core.models import (
    Buyer,
    Category,
    CompanyInfo,
    ContactPerson,
    Employee,
    NewsArticle,
    Owner,
    Property,
    PropertyImage,
    Sale,
    UserProfile,
)
from core.statistics import client_age_stats, popular_category_by_count, profitable_category, sale_amount_stats


@pytest.fixture(autouse=True)
def _use_temp_media(settings, tmp_path):
    """Сохраняет тестовые загрузки во временную папку, а не в project/media."""
    settings.MEDIA_ROOT = tmp_path / 'media'


def _gif(name='photo.gif'):
    """Возвращает минимальный валидный gif для тестовой загрузки."""
    return SimpleUploadedFile(name, b'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;', content_type='image/gif')


def _employee(username='employee_test'):
    """Создаёт сотрудника с профилем employee."""
    user = User.objects.create_user(username, password='pass', email=f'{username}@realty.by')
    UserProfile.objects.update_or_create(
        user=user,
        defaults={
            'role': UserProfile.ROLE_EMPLOYEE,
            'birth_date': date(1990, 1, 1),
            'phone': '+375 (29) 111-11-11',
            'timezone': 'Europe/Minsk',
        },
    )
    emp = Employee.objects.create(
        user=user,
        full_name='Сотрудник Тест',
        email=f'{username}@realty.by',
        phone='+375 (29) 111-11-11',
        birth_date=date(1990, 1, 1),
        hire_date=date(2020, 1, 1),
    )
    return user, emp


def _client(username='client_test'):
    """Создаёт клиента с профилем client и Buyer."""
    user = User.objects.create_user(username, password='pass', email=f'{username}@mail.by')
    UserProfile.objects.update_or_create(
        user=user,
        defaults={
            'role': UserProfile.ROLE_CLIENT,
            'birth_date': date(1995, 1, 1),
            'phone': '+375 (33) 222-22-22',
            'timezone': 'Europe/Minsk',
        },
    )
    buyer = Buyer.objects.create(
        user=user,
        full_name='Клиент Тест',
        email=f'{username}@mail.by',
        phone='+375 (33) 222-22-22',
        birth_date=date(1995, 1, 1),
    )
    return user, buyer


def _property(employee=None):
    """Создаёт объект недвижимости с категорией и владельцем."""
    cat = Category.objects.create(name='Квартиры')
    owner = Owner.objects.create(
        full_name='Владелец Тест',
        email='owner@mail.by',
        phone='+375 (29) 333-33-33',
        birth_date=date(1980, 1, 1),
    )
    prop = Property.objects.create(
        title='Квартира тестовая',
        price=Decimal('100000'),
        description='Описание тестовой квартиры',
        characteristics='50 м², 3 этаж',
        category=cat,
        is_active=True,
    )
    prop.owners.add(owner)
    if employee:
        prop.agents.add(employee)
    return prop


@pytest.mark.django_db
def test_property_form_accepts_multiple_gallery_files():
    """PropertyForm принимает список файлов в поле gallery_images."""
    cat = Category.objects.create(name='Дома')
    data = {
        'title': 'Дом с галереей',
        'price': '150000',
        'description': 'Описание дома с галереей',
        'characteristics': '120 м², участок',
        'category': cat.pk,
        'is_active': 'on',
    }
    files = {'gallery_images': [_gif('a.gif'), _gif('b.gif'), _gif('c.gif')]}
    form = PropertyForm(data=data, files=files)
    assert form.is_valid(), form.errors
    assert len(form.cleaned_data['gallery_images']) == 3


@pytest.mark.django_db
def test_employee_creates_property_with_three_gallery_images(client):
    """Сотрудник может создать объект и загрузить до трёх фото галереи с фронта."""
    user, emp = _employee('emp_gallery')
    cat = Category.objects.create(name='Дома')
    client.login(username='emp_gallery', password='pass')
    response = client.post(reverse('property_create'), {
        'title': 'Дом с тремя фото',
        'price': '180000',
        'description': 'Описание дома с тремя фотографиями',
        'characteristics': '140 м², участок 8 соток',
        'category': cat.pk,
        'is_active': 'on',
        'gallery_images': [_gif('one.gif'), _gif('two.gif'), _gif('three.gif')],
    })
    assert response.status_code == 302
    prop = Property.objects.get(title='Дом с тремя фото')
    assert prop.agents.filter(pk=emp.pk).exists()
    assert prop.gallery_images.count() == 3


@pytest.mark.django_db
def test_property_detail_renders_gallery_and_full_size_links(client):
    """Карточка объекта показывает галерею и ссылки на открытие фото без JavaScript."""
    prop = _property()
    PropertyImage.objects.create(property=prop, image=_gif('first.gif'), sort_order=1, caption='Первое фото', is_main=True)
    PropertyImage.objects.create(property=prop, image=_gif('second.gif'), sort_order=2, caption='Второе фото')
    response = client.get(reverse('property_detail', args=[prop.pk]))
    assert response.status_code == 200
    assert 'Фотографии объекта'.encode() in response.content
    assert b'target="_blank"' in response.content


@pytest.mark.django_db
def test_homefull_news_and_company_are_linked(client):
    """Новость связана с компанией homeFULL и отображает эту связь."""
    company = CompanyInfo.objects.create(
        title='homeFULL',
        about_text='Компания homeFULL занимается продажей недвижимости.',
        requisites='ООО homeFULL',
    )
    article = NewsArticle.objects.create(
        company=company,
        title='homeFULL открыл офис',
        summary='Компания homeFULL открыла офис продаж недвижимости.',
        full_text='Полный текст новости homeFULL.',
        is_published=True,
        published_at=timezone.now(),
    )
    assert NewsArticle.objects.filter(company__title='homeFULL').count() == 1
    response = client.get(reverse('news_detail', args=[article.pk]))
    assert response.status_code == 200
    assert b'homeFULL' in response.content


@pytest.mark.django_db
def test_contact_placeholder_for_missing_tenth_photo(client):
    """Если у десятого контакта нет фото, шаблон показывает заглушку."""
    ContactPerson.objects.create(
        full_name='Наталья Белова',
        position='Менеджер отдела продаж',
        duties='Консультации клиентов.',
        phone='+375 (25) 410-20-30',
        email='manager10@realty.by',
    )
    response = client.get(reverse('contacts'))
    assert response.status_code == 200
    assert b'default_contact.svg' in response.content


@pytest.mark.django_db
def test_client_purchase_and_api_scope(client):
    """Клиент покупает объект и API возвращает только его сделку."""
    employee_user, emp = _employee('emp_purchase')
    client_user, buyer = _client('buyer_purchase')
    prop = _property(employee=emp)
    client.login(username='buyer_purchase', password='pass')
    response = client.post(reverse('property_buy', args=[prop.pk]), {'confirm': 'on'})
    assert response.status_code == 302
    sale = Sale.objects.get(property=prop, buyer=buyer)
    assert sale.amount == prop.price
    api_response = client.get(reverse('api_sales'))
    assert api_response.status_code == 200
    assert len(api_response.json()['sales']) == 1
    assert api_response.json()['sales'][0]['property__title'] == prop.title


@pytest.mark.django_db
def test_sale_crud_and_statistics_helpers(client):
    """CRUD сделок и статистические функции работают для сотрудника."""
    user, emp = _employee('emp_sale')
    client_user, buyer = _client('buyer_sale')
    prop = _property(employee=emp)
    client.login(username='emp_sale', password='pass')
    create_response = client.post(reverse('sale_create'), {
        'property': prop.pk,
        'buyer': buyer.pk,
        'employee': emp.pk,
        'sale_date': '2026-01-10',
        'contract_date': '2026-01-09',
        'amount': '99000',
    })
    assert create_response.status_code == 302
    sale = Sale.objects.get(property=prop)
    assert sale_amount_stats(Sale.objects.all())['count'] == 1
    assert client_age_stats([buyer])['mean'] > 0
    assert popular_category_by_count(Property.objects.all())['cnt'] == 1
    assert profitable_category(Sale.objects.all())['total'] == Decimal('99000')
    update_response = client.post(reverse('sale_update', args=[sale.pk]), {
        'property': prop.pk,
        'buyer': buyer.pk,
        'employee': emp.pk,
        'sale_date': '2026-01-11',
        'contract_date': '2026-01-09',
        'amount': '100000',
    })
    assert update_response.status_code == 302
    assert Sale.objects.get(pk=sale.pk).amount == Decimal('100000')
    delete_response = client.post(reverse('sale_delete', args=[sale.pk]))
    assert delete_response.status_code == 302
    assert not Sale.objects.filter(pk=sale.pk).exists()
