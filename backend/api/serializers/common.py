"""Сериалайзеры приложения api."""

from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework.serializers import (CharField, IntegerField, ListField,
                                        ModelSerializer, SerializerMethodField,
                                        SlugRelatedField, ValidationError)

from recipes.models import CountOfIngredient, Ingredient, Recipe, Tag
from users.v1.serializers import UserSerializer
from users.models import ShoppingCart


class TagSerializer(ModelSerializer):
    """Сериализатор тегов."""

    class Meta:
        """Мета класс тега."""

        model = Tag
        fields = '__all__'


class IngredientSerializer(ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        """Мета класс ингредиентов."""

        model = Ingredient
        fields = '__all__'


class RecipeIngredientWriteSerializer(ModelSerializer):
    """Сериализатор RecipeIngredientWriteSerializer."""

    class Meta:
        """Мета класс RecipeIngredientWriteSerializer."""

        model = CountOfIngredient
        fields = ('id', 'amount')
        extra_kwargs = {
            'id': {
                'read_only': False,
                'error_messages': {
                    'does_not_exist': 'Такого ингредиента не существует!'
                }
            },
            'amount': {
                'error_messages': {
                    'min_value': 'Количество ингредиента не может быть '
                                 'меньше одного!'
                }
            }
        }


class RecipeIngredientReadSerializer(ModelSerializer):
    """Сериализатор RecipeIngredientReadSerializer."""

    id = IntegerField(source='ingredient.id')
    name = CharField(source='ingredient.name')
    measurement_unit = CharField(source='ingredient.measurement_unit')

    class Meta:
        """Мета класс RecipeIngredientWriteSerializer."""

        model = CountOfIngredient
        fields = '__all__'


class RecipeReadSerializer(ModelSerializer):
    """Сериализатор RecipeReadSerializer."""

    tags = TagSerializer(many=True)
    author = UserSerializer()
    ingredients = RecipeIngredientReadSerializer(many=True)
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

    class Meta:
        """Мета класс RecipeReadSerializer."""

        model = Recipe
        fields = '__all__'

    def get_is_favorited(self, obj):
        """Подписки."""
        user = self.context['request'].user
        return (
            user.is_authenticated
            and user.favorites.filter(recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        """Список покупок."""
        user = self.context['request'].user
        try:
            return (
                user.is_authenticated
                and user.shopping_cart.recipes.filter(pk__in=(obj.pk,))
                .exists()
            )
        except ShoppingCart.DoesNotExist:
            return False


class RecipeWriteSerializer(ModelSerializer):
    """Сериализатор RecipeWriteSerializer."""

    ingredients = RecipeIngredientWriteSerializer(many=True)
    tags = ListField(
        child=SlugRelatedField(
            slug_field='id',
            queryset=Tag.objects.all()
        )
    )
    image = Base64ImageField()

    class Meta:
        """Мета класс RecipeWriteSerializer."""

        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time'
        )
        extra_kwargs = {
            'cooking_time': {
                'error_messages': {
                    'min_value': 'Время приготовления не может быть '
                                 'меньше одной минуты!'
                }
            }
        }

    def validate(self, attrs):
        """Валидация."""
        if attrs['cooking_time'] < 1:
            raise ValidationError('Время приготовления не может быть меньше '
                                  'одной минуты!')
        if len(attrs['tags']) == 0:
            raise ValidationError('Рецепт не может быть без тегов!')
        if len(attrs['tags']) > len(set(attrs['tags'])):
            raise ValidationError('Теги не могут повторяться!')
        if len(attrs['ingredients']) == 0:
            raise ValidationError('Рецепт не может быть без ингредиентов!')
        id_ingredients = []
        for ingredient in attrs['ingredients']:
            if ingredient['amount'] < 1:
                raise ValidationError(
                    'Количество ингредиента не может быть меньше одного!'
                )
            id_ingredients.append(ingredient['id'])
        if len(id_ingredients) > len(set(id_ingredients)):
            raise ValidationError('Ингредиенты не могут повторяться!')
        return attrs

    def add_ingredients_and_tags(self, instance, validated_data):
        """Добавление ингредиентов и тегов."""
        ingredients, tags = (
            validated_data.pop('ingredients'), validated_data.pop('tags')
        )
        for ingredient in ingredients:
            count_of_ingredient, _ = CountOfIngredient.objects.get_or_create(
                ingredient=get_object_or_404(Ingredient, pk=ingredient['id']),
                amount=ingredient['amount']
            )
            instance.ingredients.add(count_of_ingredient)
        for tag in tags:
            instance.tags.add(tag)
        return instance

    def create(self, validated_data):
        """Создание."""
        saved = {}
        saved['ingredients'] = validated_data.pop('ingredients')
        saved['tags'] = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        return self.add_ingredients_and_tags(recipe, saved)

    def update(self, instance, validated_data):
        """Обновление."""
        instance.ingredients.clear()
        instance.tags.clear()
        instance = self.add_ingredients_and_tags(instance, validated_data)
        return super().update(instance, validated_data)
