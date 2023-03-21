"""Сериалайзеры приложения api."""
from rest_framework.serializers import ModelSerializer

from recipes.models import Recipe


class RecipeShortReadSerializer(ModelSerializer):
    """Сериализатор RecipeShortReadSerializer."""

    class Meta:
        """Мета класс RecipeShortReadSerializer."""

        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
