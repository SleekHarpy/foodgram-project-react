"""Модуль проверки разрешений."""

from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthorOrAdminOrReadOnly(BasePermission):
    """Проверка разрешений для админа и автора."""

    def has_permission(self, request, view):
        """Переопределение разрешения."""
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        """Переопределение разрешения."""
        return (
            request.method in SAFE_METHODS
            or (
                request.user.is_authenticated
                and (
                    obj.author == request.user
                    or request.user.is_superuser
                )
            )
        )
