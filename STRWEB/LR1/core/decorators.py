"""
Разграничение доступа на бэкенде (п.6, п.19).

Декораторы проверяют роль до выполнения view — дублируют проверки в шаблонах.
"""
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def role_required(*roles):
    """
    Доступ только для указанных ролей профиля или superuser.

    Args:
        *roles: 'employee', 'client' или 'superuser'.
    """

    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped(request, *args, **kwargs):
            user = request.user
            if user.is_superuser and 'superuser' in roles:
                return view_func(request, *args, **kwargs)
            profile = getattr(user, 'profile', None)
            if profile and profile.role in roles:
                return view_func(request, *args, **kwargs)
            if user.is_superuser:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied('Недостаточно прав для этой страницы.')

        return _wrapped

    return decorator


def employee_or_superuser(view_func):
    """Сотрудник или администратор."""
    return role_required('employee', 'superuser')(view_func)


def client_or_superuser(view_func):
    """Клиент или администратор."""
    return role_required('client', 'superuser')(view_func)
