from django.urls import path

from .views import (
    InventoryItemListCreateAPIView,
    InventoryItemRetrieveUpdateAPIView,
    MenuItemListCreateAPIView,
    MenuItemRetrieveUpdateDestroyAPIView,
    MenuItemReviewListCreateAPIView,
    MyRestaurantsListAPIView,
    RestaurantContentUpdateAPIView,
    RestaurantContentView,
    RestaurantCreateAPIView,
    RestaurantListAPIView,
    RestaurantRetrieveUpdateDestroyAPIView,
    RestaurantReviewListCreateAPIView,
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
    path(
        "restaurants/<uuid:restaurant_pk>/menu-items/",
        MenuItemListCreateAPIView.as_view(),
        name="menu-item-list-create",
    ),
    path(
        "restaurants/<uuid:restaurant_pk>/menu-items/<uuid:menu_item_pk>/",
        MenuItemRetrieveUpdateDestroyAPIView.as_view(),
        name="menu-item-detail",
    ),
    path(
        "restaurants/<uuid:restaurant_pk>/reviews/",
        RestaurantReviewListCreateAPIView.as_view(),
        name="restaurant-review-list-create",
    ),
    path(
        "restaurants/<uuid:restaurant_pk>/menu-items/<uuid:menu_item_pk>/reviews/",
        MenuItemReviewListCreateAPIView.as_view(),
        name="menu-item-review-list-create",
    ),
    path(
        "restaurants/<uuid:restaurant_pk>/inventory/",
        InventoryItemListCreateAPIView.as_view(),
        name="inventory-item-list-create",
    ),
    path(
        "restaurants/<uuid:restaurant_pk>/inventory/<uuid:menu_item_pk>/",
        InventoryItemRetrieveUpdateAPIView.as_view(),
        name="inventory-item-detail",
    ),
]
