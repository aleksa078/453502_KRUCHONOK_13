"""Тесты моделей и валидаторов."""
from datetime import date

import pytest
from django.core.exceptions import ValidationError

from core.models import Owner, UserProfile
from core.validators import validate_age_18_plus, validate_belarus_phone


@pytest.mark.django_db
def test_phone_validator_ok():
    validate_belarus_phone('+375 (29) 123-45-67')


def test_phone_validator_fail():
    with pytest.raises(ValidationError):
        validate_belarus_phone('80291234567')


def test_age_18_fail():
    with pytest.raises(ValidationError):
        validate_age_18_plus(date.today().replace(year=date.today().year - 10))


@pytest.mark.django_db
def test_owner_str():
    o = Owner.objects.create(
        full_name='Test',
        email='t@t.by',
        phone='+375 (29) 100-00-01',
        birth_date=date(1980, 1, 1),
    )
    assert 'Test' in str(o)
