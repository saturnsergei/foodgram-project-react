from rest_framework.permissions import BasePermission, SAFE_METHODS


class ReadOnly(BasePermission):
    """Класс разрешения, проверяющий права пользователя только на чтение."""

    def has_permission(self, request, view):
        """Проверяет разрешения на уровне запроса."""
        return request.method in SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        """Проверяет разрешения на уровне объекта."""
        return request.method in SAFE_METHODS


class IsAuthor(BasePermission):
    """Класс разрешения, проверяющий права пользователя
    на редактирование контента.
    """

    def has_permission(self, request, view):
        """Проверяет разрешения на уровне запроса."""
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Проверяет разрешения на уровне объекта."""
        return obj.author == request.user


class IsAdmin(BasePermission):
    """Класс разрешения, проверяющий права пользователя
    на администрирование.
    """

    def has_permission(self, request, view):
        """Проверяет разрешения на уровне запроса."""
        return request.user.is_authenticated and request.user.is_admin

    def has_object_permission(self, request, view, obj):
        """Проверяет разрешения на уровне объекта."""
        return request.user.is_authenticated and request.user.is_admin
