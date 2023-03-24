"""Эндпоинты api v1."""

from django.urls import path
from django.urls.conf import include
from rest_framework.routers import DefaultRouter

from api.v1.views import IngredientViewSet, RecipeViewSet, TagViewSet

router_v1 = DefaultRouter()
router_v1.register(r'tags', TagViewSet, basename='tags')
router_v1.register(r'ingredients', IngredientViewSet, basename='ingredients')
router_v1.register(r'recipes', RecipeViewSet, basename='recipes')

app_name = 'recipes'

urlpatterns = [
    path('v1/', include(router_v1.urls))
]
