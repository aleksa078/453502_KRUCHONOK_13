from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Конфигурация приложения core."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'Риэлтерское агентство'

    def ready(self):
        """Подключает signals, создающие профиль для createsuperuser."""
        import core.signals  # noqa: F401
