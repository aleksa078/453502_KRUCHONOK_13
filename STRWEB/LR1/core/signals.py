"""Signals приложения: профиль создаётся даже для superuser из createsuperuser."""
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from core.models import UserProfile


@receiver(post_save, sender=User)
def create_profile_for_manual_user(sender, instance, created, **kwargs):
    """Создаёт UserProfile для пользователя, созданного не через RegisterForm."""
    if created and not hasattr(instance, 'profile'):
        role = UserProfile.ROLE_EMPLOYEE if instance.is_superuser else UserProfile.ROLE_CLIENT
        UserProfile.objects.create(
            user=instance,
            role=role,
            timezone=getattr(settings, 'DEFAULT_USER_TIMEZONE', 'Europe/Minsk'),
        )
