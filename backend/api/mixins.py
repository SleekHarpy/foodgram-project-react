"""Миксины."""

from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet


class ListRetrieveViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    """Класс миксин."""

    pass
