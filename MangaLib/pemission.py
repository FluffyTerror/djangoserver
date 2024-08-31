from rest_framework import permissions
from rest_framework.permissions import BasePermission


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True


class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        # Проверяем, аутентифицирован ли пользователь и является ли он администратором
        return request.user and request.user.is_authenticated and request.user.is_admin