from django.urls import path

from restaurants.views import RestaurantDetailView  # Import the class-based view

from .views import (
    ManageMenuView,
    login_view,
    paid_plan_view,
    password_reset_view,
    registration_view,
    restaurant_create_view,
    restaurant_list_view,
    wildcard_view,
)

app_name = "web"

urlpatterns = [
    path("", wildcard_view, name="landing"),
    path("login/", login_view, name="login"),
    path("registration/", registration_view, name="registration"),
    path("password_reset/", password_reset_view, name="password_reset"),
    path("restaurant/create/", restaurant_create_view, name="restaurant_create"),
    path("restaurants/<uuid:pk>/", RestaurantDetailView.as_view(), name="restaurant_detail"),
    path("restaurants/", restaurant_list_view, name="restaurant_list"),
    path("restaurants/<uuid:restaurant_id>/manage-menu/", ManageMenuView.as_view(), name="manage_menu"),
    path("paid-plan/", paid_plan_view, name="paid_plan"),
    path("<str:page_name>/", wildcard_view, name="wildcard"),
]
