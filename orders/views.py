from rest_framework import generics, permissions, status, exceptions
from rest_framework.response import Response

from accounts.models import UserRole
from accounts.permissions import IsCustomer, IsRestaurantOwnerOrAdmin
from restaurants.models import Restaurant
from .models import Order
from .permissions import IsOrderOwnerOrRestaurantOwner, IsRestaurantOwner
from .serializers import OrderSerializer, OrderStatusUpdateSerializer


class OrderListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated(), IsCustomer()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            if user.role == UserRole.ADMIN:
                return Order.objects.all()
            elif user.role == UserRole.RESTAURANT_OWNER:
                return Order.objects.filter(restaurant__owner=user)
            elif user.role == UserRole.CUSTOMER:
                return Order.objects.filter(user=user)
        return Order.objects.none()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OrderRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    lookup_field = 'id'

    def get_permissions(self):
        user = self.request.user
        if user.is_authenticated:
            if user.role == UserRole.ADMIN:
                return [permissions.IsAuthenticated(), IsRestaurantOwnerOrAdmin()] # Admin can do anything
            elif user.role == UserRole.RESTAURANT_OWNER:
                return [permissions.IsAuthenticated(), IsOrderOwnerOrRestaurantOwner()] # Owner can manage their restaurant's orders
            elif user.role == UserRole.CUSTOMER:
                return [permissions.IsAuthenticated(), IsOrderOwnerOrRestaurantOwner()] # Customer can only manage their own orders
        return [permissions.IsAuthenticated()] # Default for authenticated users

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        user = self.request.user

        if user.role == UserRole.ADMIN or (user.role == UserRole.RESTAURANT_OWNER and user == instance.restaurant.owner):
            serializer = OrderStatusUpdateSerializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        elif user.role == UserRole.CUSTOMER and user == instance.user:
            # Allow customers to update their own orders, but only specific fields if needed
            # For now, disallow customer updates other than status by owner
            return Response({"detail": "Customers can only view their orders."}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)

    def perform_destroy(self, instance):
        user = self.request.user
        if user.role == UserRole.ADMIN:
            instance.delete()
        elif user.role == UserRole.CUSTOMER and instance.status == 'pending' and user == instance.user:
            instance.delete()
        else:
            raise exceptions.PermissionDenied("Only pending orders can be cancelled by the order owner, or any order by an admin.")