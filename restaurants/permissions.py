from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """Custom permission to only allow owners of an object to edit it."""

    def has_object_permission(self, request, view, obj):
        # Write permissions are only allowed to the owner of the restaurant.
        return obj.owner == request.user


class IsRestaurantOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of a restaurant to edit its menu items.
    Read-only access is allowed to anyone.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the restaurant.
        return obj.restaurant.owner == request.user


class IsInventoryItemOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of the restaurant associated with an
    InventoryItem to view or edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Only the owner of the restaurant associated with the InventoryItem's MenuItem
        # can view or edit it.
        return obj.menu_item.restaurant.owner == request.user
