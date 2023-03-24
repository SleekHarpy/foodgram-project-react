"""Модели приложения users."""

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """Модель пользователя."""

    USER = 'user'
    ADMIN = 'admin'
    USER_ROLE = [
        ('user', USER),
        ('admin', ADMIN),
    ]

    email = models.EmailField('Почта', max_length=254, unique=True)
    username = models.CharField('Никнейм', max_length=150)
    first_name = models.CharField('Имя', max_length=150,)
    last_name = models.CharField('Фамилия', max_length=150)
    password = models.CharField('Пароль', max_length=150)
    is_superuser = models.BooleanField('Администратор', default=False)
    is_blocked = models.BooleanField('Заблокирован', default=False)
    role = models.CharField(
        'Роль', max_length=30, choices=USER_ROLE, default='user'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    class Meta:
        """Мета класс пользователя."""

        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('-pk',)

    def __str__(self):
        """Описание пользователя."""
        return self.username

    @property
    def is_staff(self):
        """Поверка на суперпользователя."""
        return self.is_superuser


class Subscribe(models.Model):
    """Модель подписки."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribing',
        verbose_name='Автор'
    )

    class Meta:
        """Мета класс подписки."""

        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_subscribe',
            ),
        )

    def __str__(self):
        """Описание класса подписки."""
        return f'{self.user} -> {self.author}'


class ShoppingCart(models.Model):
    """Модель списка покупок."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь',
    )
    recipes = models.ManyToManyField(
        'recipes.Recipe',
        related_name='in_shopping_cart',
        verbose_name='Рецепты',
    )

    class Meta:
        """Мета класс списка покупок."""

        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        """Описание класса списка покупок."""
        return f'{self.user}'
