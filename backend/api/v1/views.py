"""Классы представления приложения api."""

from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED,
                                   HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST)
from rest_framework.viewsets import ModelViewSet

from api.v1.filters import IngredientSearchFilter, RecipeFilter
from api.v1.mixins import ListRetrieveViewSet
from api.serializers.common import (IngredientSerializer, RecipeReadSerializer,
                                    RecipeWriteSerializer, TagSerializer)
from api.serializers.nested import RecipeShortReadSerializer
from foodgram.pagination import LimitPageNumberPagination
from foodgram.permissions import IsAuthorOrAdminOrReadOnly
from recipes.models import Favorite, Ingredient, Recipe, Tag


class TagViewSet(ListRetrieveViewSet):
    """Класс представления тега."""

    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    http_method_names = ('get',)


class IngredientViewSet(ListRetrieveViewSet):
    """Класс представления ингредиента."""

    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientSearchFilter
    queryset = Ingredient.objects.all()
    http_method_names = ('get',)


class RecipeViewSet(ModelViewSet):
    """Класс представления рецепта."""

    pagination_class = LimitPageNumberPagination
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    queryset = Recipe.objects.all()
    http_method_names = ('get', 'post', 'put', 'patch', 'delete')

    def get_serializer_class(self):
        """Переопределение получения рецептов."""
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        """Переопределение создания рецептов."""
        serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        """Создание рецептов."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        serializer = RecipeReadSerializer(
            instance=serializer.instance,
            context={'request': self.request}
        )
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=HTTP_201_CREATED, headers=headers
        )

    def update(self, request, *args, **kwargs):
        """Переопределение обновления рецептов."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        serializer = RecipeReadSerializer(
            instance=serializer.instance,
            context={'request': self.request}
        )
        return Response(
            serializer.data, status=HTTP_200_OK
        )

    def add_to_favorite(self, request, recipe):
        """Добавление в избранное рецептов."""
        try:
            Favorite.objects.create(user=request.user, recipe=recipe)
        except IntegrityError:
            return Response(
                {'errors': 'Вы уже подписаны!'},
                status=HTTP_400_BAD_REQUEST
            )
        serializer = RecipeShortReadSerializer(recipe)
        return Response(
            serializer.data,
            status=HTTP_201_CREATED
        )

    def delete_from_favorite(self, request, recipe):
        """Удаление рецептов из избранных."""
        favorite = Favorite.objects.filter(user=request.user, recipe=recipe)
        if not favorite.exists():
            return Response(
                {'errors': 'Подписки не существует!'},
                status=HTTP_400_BAD_REQUEST
            )
        favorite.delete()
        return Response(status=HTTP_204_NO_CONTENT)

    @action(
        methods=('post', 'delete'),
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        """Добавление или удаление рецептов из избранных."""
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            return self.add_to_favorite(request, recipe)
        return self.delete_from_favorite(request, recipe)
