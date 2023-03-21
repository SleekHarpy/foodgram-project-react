"""Админ панель."""

from django.contrib.admin import ModelAdmin, display, register

from .models import CountOfIngredient, Favorite, Ingredient, Recipe, Tag


@register(Tag)
class TagAdmin(ModelAdmin):
    """Теги админка."""

    list_display = ('id', 'name', 'slug', 'color')
    search_fields = ('name', 'slug')
    ordering = ('color',)
    empty_value_display = '< Пусто >'


@register(Ingredient)
class IngredientAdmin(ModelAdmin):
    """Ингредиенты админка."""

    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)
    ordering = ('measurement_unit',)
    empty_value_display = '< Пусто >'


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    """Рецепты админка."""

    list_display = ('name', 'author')
    list_filter = ('name', 'author', 'tags')
    readonly_fields = ('added_in_favorites',)
    empty_value_display = '< Пусто >'

    @display(description='Общее число добавлений в избранное')
    def added_in_favorites(self, obj):
        """Добавленные в избранное."""
        return obj.favorites.count()


@register(CountOfIngredient)
class CountOfIngredientAdmin(ModelAdmin):
    """Подсчёт ингредиентов админка."""

    list_display = ('id', 'ingredient', 'amount', 'get_measurement_unit',
                    'get_recipes_count')
    readonly_fields = ('get_measurement_unit',)
    list_filter = ('ingredient',)
    ordering = ('ingredient',)
    empty_value_display = '< Пусто >'

    @display(description='Единица измерения')
    def get_measurement_unit(self, obj):
        """Получение единиц измерения."""
        try:
            return obj.ingredient.measurement_unit
        except CountOfIngredient.ingredient.RelatedObjectDoesNotExist:
            return '< Пусто >'

    @display(description='Количество ссылок в рецептах')
    def get_recipes_count(self, obj):
        """Получение количества рецептов."""
        return obj.recipes.count()


@register(Favorite)
class FavoriteAdmin(ModelAdmin):
    """Избранное админка."""

    list_display = ('user', 'recipe')
    list_filter = ('user', 'recipe')
    empty_value_display = '< Пусто >'
