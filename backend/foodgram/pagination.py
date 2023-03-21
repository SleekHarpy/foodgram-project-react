"""Пагинация."""

from rest_framework.pagination import PageNumberPagination


class LimitPageNumberPagination(PageNumberPagination):
    """Лимит элементов на странице."""

    page_size_query_param = 'limit'
    page_size = 10
