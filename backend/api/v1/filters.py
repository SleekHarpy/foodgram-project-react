"""Фильтр."""

from django.db.models import IntegerField, Value
from django_filters.rest_framework import (AllValuesMultipleFilter,
                                           BooleanFilter, CharFilter,
                                           FilterSet)

from recipes.models import Ingredient, Recipe
from users.models import ShoppingCart


class IngredientSearchFilter(FilterSet):
    """Фильтр для ингредиентов."""

    name = CharFilter(method='search_by_name')

    class Meta:
        """Мета класс фильтра ингредиентов."""

        model = Ingredient
        fields = ('name',)

    def search_by_name(self, queryset, name, value):
        """Поиск по имени."""
        if not value:
            return queryset
        start_with_queryset = (
            queryset.filter(name__istartswith=value).annotate(
                order=Value(0, IntegerField())
            )
        )
        contain_queryset = (
            queryset.filter(name__icontains=value).exclude(
                pk__in=(ingredient.pk for ingredient in start_with_queryset)
            ).annotate(
                order=Value(1, IntegerField())
            )
        )
        return start_with_queryset.union(contain_queryset).order_by('order')


class RecipeFilter(FilterSet):
    """Фильтр для рецептов."""

    is_favorited = BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = BooleanFilter(method='get_is_in_shopping_cart')
    tags = AllValuesMultipleFilter(field_name='tags__slug')

    class Meta:
        """Мета класс фильтра рецептов."""

        model = Recipe
        fields = ('author', 'tags')

    def get_is_favorited(self, queryset, name, value):
        """Получение избранных товаров."""
        if not value:
            return queryset
        return queryset.filter(favorites__user=self.request.user)

    def get_is_in_shopping_cart(self, queryset, name, value):
        """Получение рецептов в списке покупок."""
        if not value:
            return queryset
        try:
            recipes = (
                self.request.user.shopping_cart.recipes.all()
            )
        except ShoppingCart.DoesNotExist:
            return queryset
        return queryset.filter(
            pk__in=(recipe.pk for recipe in recipes)
        )
