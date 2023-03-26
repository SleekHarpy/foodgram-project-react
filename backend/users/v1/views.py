"""Классы представления приложения users."""

from django.db.models import Sum
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import TokenCreateView, UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.serializers.nested import RecipeShortReadSerializer
from foodgram.pagination import LimitPageNumberPagination
from recipes.models import Recipe
from users.models import ShoppingCart, Subscribe, User

from .serializers import SubscriptionSerializer


class TokenCreateWithCheckBlockStatusView(TokenCreateView):
    """Создание токена."""

    def _action(self, serializer):
        """Проверка аккаунта."""
        if serializer.user.is_blocked:
            return Response(
                {'errors': 'Аккаунт заблокирован'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super()._action(serializer)


class UserSubscribeViewSet(UserViewSet):
    """Подписка пользователя."""

    pagination_class = LimitPageNumberPagination
    lookup_url_kwarg = 'user_id'

    def get_subscription_serializer(self, *args, **kwargs):
        """Получение подписки."""
        kwargs.setdefault('context', self.get_serializer_context())
        return SubscriptionSerializer(*args, **kwargs)

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        """Подписки."""
        self.get_serializer
        queryset = User.objects.filter(subscribing__user=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_subscription_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_subscription_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create_subscribe(self, request, author):
        """Создание подписки."""
        subscribe = Subscribe.objects.create(
            user=request.user,
            author=author,
        )
        serializer = self.get_subscription_serializer(subscribe.author)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_subscribe(self, request, author):
        """Удаление подписки."""
        try:
            Subscribe.objects.get(user=request.user, author=author).delete()
        except Subscribe.DoesNotExist:
            return Response(
                {'errors': 'Нельзя отписаться от данного пользователя,'
                           ' если вы не подписаны на него!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        methods=('post', 'delete'),
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, user_id=None):
        """Подписка."""
        try:
            author = get_object_or_404(User, pk=user_id)
        except Http404:
            return Response(
                {'detail': 'Пользователь не найден!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.method == 'POST':
            return self.create_subscribe(request, author)
        return self.delete_subscribe(request, author)


class ShoppingCartViewSet(GenericViewSet):
    """Список покупок."""

    NAME = 'ingredients__ingredient__name'
    MEASUREMENT_UNIT = 'ingredients__ingredient__measurement_unit'
    permission_classes = (IsAuthenticated,)
    serializer_class = RecipeShortReadSerializer
    queryset = ShoppingCart.objects.all()
    http_method_names = ('get', 'post', 'delete')

    def generate_shopping_cart_data(self, request):
        """Генерация данных для списка покупок."""
        recipes = (
            request.user.shopping_cart.recipes.prefetch_related('ingredients')
        )
        return (
            recipes.order_by(self.NAME)
            .values(
                self.NAME,
                self.MEASUREMENT_UNIT
            )
            .annotate(total=Sum('ingredients__amount'))
        )

    def generate_ingredients_content(self, ingredients):
        """Генерация ингредиентов."""
        content = ''
        for ingredient in ingredients:
            content += (
                f'{ingredient[self.NAME]}'
                f'{ingredient[self.MEASUREMENT_UNIT]}'
                f' - {ingredient["total"]}\r\n'
            )
        return content

    @action(detail=False)
    def download_shopping_cart(self, request):
        """Скачивание списка покупок."""
        try:
            ingredients = self.generate_shopping_cart_data(request)
        except ShoppingCart.DoesNotExist:
            return Response(
                {'errors': 'Список покупок не существует!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        content = self.generate_ingredients_content(ingredients)
        response = HttpResponse(
            content, content_type='text/plain, charset=utf8'
        )
        response['Content-Disposition'] = 'attachment; filename=shopping_list'
        return response

    def add_to_shopping_cart(self, request, recipe, shopping_cart):
        """Добавление в список покупок."""
        if shopping_cart.recipes.filter(pk__in=(recipe.pk,)).exists():
            return Response(
                {'errors': 'Рецепт уже добавлен!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        shopping_cart.recipes.add(recipe)
        serializer = self.get_serializer(recipe)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def remove_from_shopping_cart(self, request, recipe, shopping_cart):
        """Удаление из списка покупок."""
        if not shopping_cart.recipes.filter(pk__in=(recipe.pk,)).exists():
            return Response(
                {'errors': 'Нельзя удалить рецепт из списка покупок, '
                           'которого нет в списке покупок!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        shopping_cart.recipes.remove(recipe)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=('post', 'delete'), detail=True)
    def shopping_cart(self, request, pk=None):
        """Список покупок."""
        recipe = get_object_or_404(Recipe, pk=pk)
        shopping_cart = (
            ShoppingCart.objects.get_or_create(user=request.user)[0]
        )
        if request.method == 'POST':
            return self.add_to_shopping_cart(request, recipe, shopping_cart)
        return self.remove_from_shopping_cart(request, recipe, shopping_cart)
