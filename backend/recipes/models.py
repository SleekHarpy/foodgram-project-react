"""Модели приложения recipes."""

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse

MIN_INGREDIENT = 1
MIN_COOKING_TIME = 1

User = get_user_model()


class Tag(models.Model):
    """Модель тега."""

    name = models.CharField('Название', max_length=200)
    color = models.CharField('Цвет в HEX', max_length=7)
    slug = models.SlugField('Идентификатор', max_length=200)

    class Meta:
        """Мета класс тега."""

        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        """Описание тега."""
        return self.name

    def get_absolute_url(self):
        """Получение абсолютного URL адреса."""
        return reverse('tag', args=[self.slug])


class Ingredient(models.Model):
    """Модель ингредиента."""

    name = models.CharField('Название', max_length=200)
    measurement_unit = models.CharField('Единица измерения', max_length=200)

    class Meta:
        """Мета класс ингредиента."""

        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        """Описание ингредиента."""
        return self.name


class Recipe(models.Model):
    """Модель рецепта."""

    name = models.CharField('Название', max_length=200)
    text = models.TextField('Описание')
    ingredients = models.ManyToManyField(
        'CountOfIngredient',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги'
    )
    image = models.ImageField('Изображение')
    cooking_time = models.PositiveIntegerField(
        'Время готовки',
        validators=(MinValueValidator(
            MIN_COOKING_TIME,
            message='Время приготовления не может быть меньше одной минуты!'
        ),)
    )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recipes',
        verbose_name='Автор'
    )

    class Meta:
        """Мета класс рецепта."""

        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pk',)

    def __str__(self):
        """Описание рецепта."""
        return f'{self.name} ({self.author})'

    def get_absolute_url(self):
        """Получение абсолютного URL адреса."""
        return reverse('recipe', args=[self.pk])


class CountOfIngredient(models.Model):
    """Модель подсчёта ингредиентов."""

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='count_in_recipes',
        verbose_name='Ингредиент',
    )
    amount = models.PositiveIntegerField(
        'Количество',
        validators=(MinValueValidator(
            MIN_INGREDIENT,
            message='Количество ингредиентов не может быть меньше одного!'
        ),)
    )

    class Meta:
        """Мета класс модели подсчёта ингредиентов."""

        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        constraints = (
            models.UniqueConstraint(
                fields=('ingredient', 'amount'),
                name='unique_ingredient_amount'
            ),
        )

    def __str__(self):
        """Описание класса подсчёта ингредиентов."""
        return (
            f'{self.ingredient.name} - {self.amount} '
            f'({self.ingredient.measurement_unit})'
        )


class Favorite(models.Model):
    """Модель избранного."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт'
    )

    class Meta:
        """Мета класс избранного."""

        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe',),
                name='unique_user_recipe',
            ),
        )

    def __str__(self):
        """Описание избранного."""
        return f'{self.user} -> {self.recipe}'
