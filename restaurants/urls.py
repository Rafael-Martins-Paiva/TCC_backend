from django.urls import path

from .views import (
    MyRestaurantsListAPIView,
    RestaurantContentUpdateAPIView,
    RestaurantContentView,
    RestaurantCreateAPIView,
    RestaurantListAPIView,
    RestaurantRetrieveUpdateDestroyAPIView,
    RestaurantSubdomainView,
)

urlpatterns = [
    path("", RestaurantSubdomainView.as_view(), name="restaurant-subdomain-view"),
    path("restaurants/", RestaurantListAPIView.as_view(), name="restaurant-list"),
    path("restaurants/my-restaurants/", MyRestaurantsListAPIView.as_view(), name="my-restaurant-list"),
    path("restaurants/create/", RestaurantCreateAPIView.as_view(), name="restaurant-create"),
    path("restaurants/<uuid:pk>/", RestaurantRetrieveUpdateDestroyAPIView.as_view(), name="restaurant-detail"),
    path("restaurants/<uuid:pk>/content/", RestaurantContentUpdateAPIView.as_view(), name="restaurant-content-update"),
    path("restaurants/<uuid:pk>/content/view/", RestaurantContentView.as_view(), name="restaurant-content-view"),
]
