from datetime import date

import pytest

from core.forms import RegisterForm


@pytest.mark.django_db
def test_register_form_invalid_age():
    form = RegisterForm(data={
        'username': 'u1',
        'email': 'u1@t.by',
        'password1': 'ComplexPass123!',
        'password2': 'ComplexPass123!',
        'birth_date': date.today().replace(year=date.today().year - 5),
        'phone': '+375 (29) 100-00-01',
        'role': 'client',
        'timezone': 'Europe/Minsk',
    })
    assert not form.is_valid()
