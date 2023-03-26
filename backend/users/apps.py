"""Конфиг приложения users."""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Класс конфига приложения users."""

    name = 'users'
    verbose_name = 'Пользователи'
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        """Чтение."""
