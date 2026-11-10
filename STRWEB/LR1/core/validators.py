"""
Валидаторы для форм и моделей (требования п.12, п.13, п.19).

ДР (дата рождения): проверка 18+ на уровне формы и модели.
Телефон: формат +375 (29) XXX-XX-XX.
"""
import re
from datetime import date

from django.core.exceptions import ValidationError
from django.utils import timezone


PHONE_REGEX = re.compile(
    r'^\+375\s\((29|33|44|25)\)\s\d{3}-\d{2}-\d{2}$'
)


def validate_belarus_phone(value):
    """
    Проверяет телефон клиента в формате +375 (29) XXX-XX-XX.

    Args:
        value: строка телефона.

    Raises:
        ValidationError: если формат не совпадает.
    """
    if not PHONE_REGEX.match(value or ''):
        raise ValidationError(
            'Телефон должен быть в формате +375 (29) XXX-XX-XX '
            '(код оператора: 29, 33, 44 или 25).'
        )


def validate_age_18_plus(birth_date):
    """
    Проверяет, что человеку исполнилось 18 лет на текущую дату.

    Args:
        birth_date: date — дата рождения.

    Raises:
        ValidationError: если возраст меньше 18.
    """
    if birth_date is None:
        return
    today = timezone.now().date()
    age = today.year - birth_date.year - (
        (today.month, today.day) < (birth_date.month, birth_date.day)
    )
    if age < 18:
        raise ValidationError('Клиенты и сотрудники должны быть старше 18 лет.')
