from rest_framework import permissions


class IsRestaurantOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a restaurant to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the restaurant.
        return obj.owner == request.user


class IsOrderOwnerOrRestaurantOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an order or the owner of the associated restaurant to access it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are only allowed to the owner of the order or the owner of the associated restaurant.
        return obj.user == request.user or obj.restaurant.owner == request.user