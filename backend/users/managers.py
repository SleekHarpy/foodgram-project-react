"""User manager."""

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password


class UserManager(BaseUserManager):
    """Менеджер пользователя."""

    def create_user(self, username, email, password, **extra_fields):
        """Создание пользователя."""
        if not username:
            raise ValueError('Имя пользователя не может быть пустым!')
        if not email:
            raise ValueError('Почта не может быть пустой!')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.password = make_password(password)
        user.save()
        return user

    def create_superuser(self, username, email, password, **extra_fields):
        """Создание суперпользователя."""
        extra_fields.setdefault('is_superuser', True)

        if not extra_fields.get('is_superuser'):
            raise ValueError(
                'Суперпользователь должен иметь is_superuser=True!'
            )
        return self.create_user(username, email, password, **extra_fields)
