from rest_framework.permissions import BasePermission

from accounts.models import UserRole


class IsAdminUser(BasePermission):
    """Allows access only to admin users."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == UserRole.ADMIN)


class IsRestaurantOwner(BasePermission):
    """Allows access only to restaurant owners."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == UserRole.RESTAURANT_OWNER)


class IsCustomer(BasePermission):
    """Allows access only to regular customers."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == UserRole.CUSTOMER)


class IsRestaurantOwnerOrAdmin(BasePermission):
    """Allows access only to restaurant owners or admin users."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.role == UserRole.RESTAURANT_OWNER or request.user.role == UserRole.ADMIN)
        )
