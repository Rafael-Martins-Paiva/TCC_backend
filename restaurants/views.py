from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView, TemplateView
from rest_framework import generics, permissions, serializers, status
from rest_framework.parsers import FormParser, MultiPartParser
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from rest_framework.views import APIView

from orders.models import Order
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from accounts.permissions import IsRestaurantOwnerOrAdmin
from .models import InventoryItem, MenuItem, Restaurant, Review
from .permissions import IsInventoryItemOwner, IsOwner, IsRestaurantOwnerOrReadOnly, IsRestaurantOwnerForCreate, IsInventoryItemOwnerForCreate
from .serializers import (
    InventoryItemSerializer,
    MenuItemSerializer,
    RestaurantContentSerializer,
    RestaurantSerializer,
    ReviewSerializer,
)
from .services import UpdateRestaurantContentService, GenerateRestaurantQRCodeUseCase
from restaurants.domain.services import RestaurantURLService
from core.qr_codes import QRCodeGenerator


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

    def get_permissions(self):
        if self.request.method == "GET":
            # Allow any authenticated user to view a restaurant.
            return [permissions.IsAuthenticated()]
        # Only the owner or admin can update or delete.
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
        service.execute(restaurant=instance, html_content=serializer.validated_data["website_content"])
        return Response(serializer.data)


class RestaurantContentView(generics.RetrieveAPIView):
    """Serves the raw HTML content of a restaurant's website."""

    queryset = Restaurant.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        return HttpResponse(instance.website_content, content_type="text/html")


class RestaurantSubdomainView(RestaurantContentView):
    """Serves the raw HTML content of a restaurant's website based on the subdomain."""

    def get_object(self):
        host = self.request.META.get("HTTP_HOST", "")
        # Assuming host is like 'subdomain.localtest.me:8000' or 'subdomain.localtest.me'
        if ".localtest.me" in host:
            subdomain_part = host.split(".localtest.me")[0]
            restaurant_name = subdomain_part.split(":")[0]  # Remove port if present
        else:
            restaurant_name = None  # Or raise an error if not a subdomain request

        print(f"RestaurantSubdomainView: Extracted restaurant name from host: {restaurant_name}")

        if not restaurant_name:
            raise Http404("Restaurant name could not be extracted from subdomain.")

        obj = get_object_or_404(Restaurant, name__iexact=restaurant_name)
        self.check_object_permissions(self.request, obj)
        return obj

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if not instance.website_content:
                return HttpResponse(
                    f"<h1>Welcome to {instance.name}'s subdomain!</h1><p>No website content has been added yet.</p>",
                    content_type="text/html",
                )
            return HttpResponse(instance.website_content, content_type="text/html")
        except Http404:
            return render(request, "web/404.html", status=404)


class MenuItemListCreateAPIView(generics.ListCreateAPIView):
    """List all menu items for a restaurant, or create a new one."""

    authentication_classes = [SessionAuthentication]
    serializer_class = MenuItemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsRestaurantOwnerForCreate]
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        restaurant_pk = self.kwargs["restaurant_pk"]
        return MenuItem.objects.filter(restaurant__pk=restaurant_pk)

    def perform_create(self, serializer):
        restaurant_pk = self.kwargs["restaurant_pk"]
        restaurant = get_object_or_404(Restaurant, pk=restaurant_pk)
        serializer.save(restaurant=restaurant)


class MenuItemRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a menu item."""

    authentication_classes = [SessionAuthentication]
    serializer_class = MenuItemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsRestaurantOwnerOrReadOnly]
    parser_classes = (MultiPartParser, FormParser)
    lookup_url_kwarg = "menu_item_pk"

    def get_queryset(self):
        restaurant_pk = self.kwargs["restaurant_pk"]
        return MenuItem.objects.filter(restaurant__pk=restaurant_pk)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=False) # Do not raise exception immediately
        if serializer.errors:
            print("MenuItem Update Validation Errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        self.perform_update(serializer)
        return Response(serializer.data)


class RestaurantDetailView(DetailView):
    model = Restaurant
    template_name = "web/restaurant_detail.html"
    context_object_name = "restaurant"
    pk_url_kwarg = "pk"

    def get_queryset(self):
        return super().get_queryset().select_related("owner")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        restaurant = self.get_object()
        context["menu_items"] = restaurant.menu_items.all().prefetch_related("reviews__author")
        context["restaurant_reviews"] = restaurant.reviews.all().select_related("author")
        return context


class RestaurantReviewListCreateAPIView(generics.ListCreateAPIView):
    """List all reviews for a restaurant, or create a new one."""

    authentication_classes = [SessionAuthentication]
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        restaurant_pk = self.kwargs["restaurant_pk"]
        return Review.objects.filter(restaurant__pk=restaurant_pk)

    def perform_create(self, serializer):
        restaurant = get_object_or_404(Restaurant, pk=self.kwargs["restaurant_pk"])
        serializer.save(author=self.request.user, restaurant=restaurant)


class MenuItemReviewListCreateAPIView(generics.ListCreateAPIView):
    """List all reviews for a menu item, or create a new one."""

    authentication_classes = [SessionAuthentication]
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        menu_item_pk = self.kwargs["menu_item_pk"]
        return Review.objects.filter(menu_item__pk=menu_item_pk)

    def perform_create(self, serializer):
        menu_item = get_object_or_404(MenuItem, pk=self.kwargs["menu_item_pk"])
        serializer.save(author=self.request.user, menu_item=menu_item)


class InventoryItemListCreateAPIView(generics.ListCreateAPIView):
    """
    Lists all inventory items for a restaurant's menu items.
    Allows creating an InventoryItem for a MenuItem if one doesn't exist.
    """

    authentication_classes = [SessionAuthentication]
    serializer_class = InventoryItemSerializer
    permission_classes = [permissions.IsAuthenticated, IsInventoryItemOwnerForCreate]

    def get_queryset(self):
        restaurant_pk = self.kwargs["restaurant_pk"]
        return InventoryItem.objects.filter(menu_item__restaurant__pk=restaurant_pk)

    def perform_create(self, serializer):
        menu_item_pk = self.request.data.get("menu_item")
        if not menu_item_pk:
            raise serializers.ValidationError({"menu_item": "This field is required."})

        menu_item = get_object_or_404(MenuItem, pk=menu_item_pk)

        # Check if an InventoryItem already exists for this MenuItem
        if InventoryItem.objects.filter(menu_item=menu_item).exists():
            raise serializers.ValidationError({"menu_item": "Inventory item already exists for this menu item."})

        serializer.save(menu_item=menu_item)


class InventoryItemRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    """
    Retrieves and updates a specific inventory item.
    """

    authentication_classes = [SessionAuthentication]
    serializer_class = InventoryItemSerializer
    permission_classes = [permissions.IsAuthenticated, IsInventoryItemOwner]

    lookup_field = "menu_item__pk"  # Look up by menu_item's primary key
    lookup_url_kwarg = "menu_item_pk"

    def get_queryset(self):
        restaurant_pk = self.kwargs["restaurant_pk"]
        return InventoryItem.objects.filter(menu_item__restaurant__pk=restaurant_pk)

    def get_object(self):
        # Override get_object to use the custom lookup_field and check permissions
        queryset = self.filter_queryset(self.get_queryset())
        filter_kwargs = {self.lookup_field: self.kwargs[self.lookup_url_kwarg]}
        obj = get_object_or_404(queryset, **filter_kwargs)
        self.check_object_permissions(self.request, obj)
        return obj


@method_decorator(login_required, name="dispatch")
class RestaurantOrderManagementView(TemplateView):
    template_name = "restaurants/order_management.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_restaurants = self.request.user.restaurants.all()
        
        # Fetch orders for all restaurants owned by the current user
        # Exclude completed orders from the main list
        active_orders = Order.objects.filter(
            restaurant__in=user_restaurants
        ).exclude(status='completed').order_by('created_at').prefetch_related('items__menu_item')

        # Group orders by restaurant
        orders_by_restaurant = {}
        for order in active_orders:
            if order.restaurant.name not in orders_by_restaurant:
                orders_by_restaurant[order.restaurant.name] = []
            orders_by_restaurant[order.restaurant.name].append(order)

        context['orders_by_restaurant'] = orders_by_restaurant
        return context


class RestaurantQRCodeAPIView(APIView):
    """
    Generates a QR code for a specific restaurant.
    """
    authentication_classes = [SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get(self, request, pk, *args, **kwargs):
        restaurant = get_object_or_404(Restaurant, pk=pk)
        self.check_object_permissions(request, restaurant)

        # Construct base_url dynamically from the request
        # This assumes the API is accessed via a standard HTTP/S request
        base_url = request.build_absolute_uri('/')[:-1] # Remove trailing slash

        url_service = RestaurantURLService()
        qr_generator = QRCodeGenerator()
        use_case = GenerateRestaurantQRCodeUseCase(url_service, qr_generator)

        qr_code_image_bytes = use_case.execute(restaurant_id=restaurant.pk, base_url=base_url)

        return HttpResponse(qr_code_image_bytes, content_type='image/png')