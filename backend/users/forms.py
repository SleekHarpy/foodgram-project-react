"""Формы."""

from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import User


class CustomUserCreationForm(UserCreationForm):
    """Форма создания пользователя."""

    class Meta:
        """Мета класс создания пользователя."""

        model = User
        fields = ('email', 'username', 'first_name', 'last_name')


class CustomUserChangeForm(UserChangeForm):
    """Форма редактирования пользователя."""

    class Meta:
        """Мета класс создания пользователя."""

        model = User
        fields = ('email', 'username', 'first_name', 'last_name')
