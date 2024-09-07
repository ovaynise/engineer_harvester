from rest_framework import permissions


class AuthorOrReadOnly(permissions.BasePermission):
    """Разрешение позволяющее редактировать записи только их авторам."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user


class AdminOnly(permissions.BasePermission):
    """Разрешение, позволяющее доступ к записи только
    администраторам для GET-запросов."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_staff
        return obj.author == request.user
