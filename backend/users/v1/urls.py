"""Эндпоинты users."""

from django.urls import include, path
from djoser.views import TokenDestroyView
from rest_framework.routers import DefaultRouter

from .views import (ShoppingCartViewSet, TokenCreateWithCheckBlockStatusView,
                    UserSubscribeViewSet)

router_v1 = DefaultRouter()
router_v1.register(r'users', UserSubscribeViewSet, basename='users')
router_v1.register(r'recipes', ShoppingCartViewSet, basename='shopping_cart')

app_name = 'users'

authorization = [
    path(
        'token/login/',
        TokenCreateWithCheckBlockStatusView.as_view(),
        name='login'
    ),
    path('token/logout/', TokenDestroyView.as_view(), name='logout')
]

urlpatterns = [
    path('v1/auth/', include(authorization)),
    path('v1/', include(router_v1.urls)),
]
