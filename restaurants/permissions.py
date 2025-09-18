from rest_framework import permissions
from restaurants.models import Restaurant, MenuItem

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


class IsRestaurantOwnerForCreate(permissions.BasePermission):
    """
    Custom permission to only allow owners of a restaurant to create menu items for it.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        if not request.user.is_authenticated:
            return False

        restaurant_pk = view.kwargs.get('restaurant_pk')
        if not restaurant_pk:
            return False

        try:
            restaurant = Restaurant.objects.get(pk=restaurant_pk)
        except Restaurant.DoesNotExist:
            return False

        return restaurant.owner == request.user

    def has_object_permission(self, request, view, obj):
        return obj.restaurant.owner == request.user


class IsInventoryItemOwnerForCreate(permissions.BasePermission):
    """
    Custom permission to only allow owners of the restaurant associated with a
    MenuItem to create InventoryItems for it.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        menu_item_pk = request.data.get('menu_item')
        if not menu_item_pk:
            # If menu_item is not provided in data, let serializer handle validation
            return True

        try:
            menu_item = MenuItem.objects.get(pk=menu_item_pk)
        except MenuItem.DoesNotExist:
            return False

        return menu_item.restaurant.owner == request.user
