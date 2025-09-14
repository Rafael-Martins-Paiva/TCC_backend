from django.urls import path

from .views import (
    login_view,
    paid_plan_view,
    password_reset_view,
    registration_view,
    restaurant_create_view,
    restaurant_detail_view,
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
    path("restaurant/<uuid:restaurant_id>/", restaurant_detail_view, name="restaurant_detail"),
    path("restaurants/", restaurant_list_view, name="restaurant_list"),
    path("paid-plan/", paid_plan_view, name="paid_plan"),
    path("<str:page_name>/", wildcard_view, name="wildcard"),
]
