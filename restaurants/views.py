from django.http import HttpResponse
from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from .models import Restaurant
from .serializers import RestaurantSerializer, RestaurantContentSerializer
from .services import UpdateRestaurantContentService
from .permissions import IsOwner

class RestaurantListAPIView(generics.ListAPIView):
    """Lists all restaurants for any user."""
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [permissions.AllowAny]

class MyRestaurantsListAPIView(generics.ListAPIView):
    """Lists restaurants owned by the currently authenticated user."""
    serializer_class = RestaurantSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Restaurant.objects.filter(owner=self.request.user)

class RestaurantCreateAPIView(generics.CreateAPIView):
    """Creates a new restaurant owned by the authenticated user."""
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        if not self.request.user.has_paid_plan:
            raise PermissionDenied("You must have a paid plan to create a restaurant.")
        # The owner is automatically set to the logged-in user.
        serializer.save(owner=self.request.user)

class RestaurantRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, Update or Delete a restaurant instance."""
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_permissions(self):
        if self.request.method == 'GET':
            # Allow any authenticated user to view a restaurant.
            return [permissions.IsAuthenticated()]
        # But only the owner can update or delete.
        return [permissions.IsAuthenticated(), IsOwner()]

class RestaurantContentUpdateAPIView(generics.UpdateAPIView):
    """Updates the website content for a restaurant."""
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantContentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        service = UpdateRestaurantContentService()
        service.execute(restaurant=instance, html_content=serializer.validated_data['website_content'])
        return Response(serializer.data)

class RestaurantContentView(generics.RetrieveAPIView):
    """Serves the raw HTML content of a restaurant's website."""
    queryset = Restaurant.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        return HttpResponse(instance.website_content, content_type='text/html')
