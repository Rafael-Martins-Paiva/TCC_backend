from django.contrib import admin
from django.urls import include, path

"""from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)"""

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/auth/", include("dj_rest_auth.urls")),
    path("api/v1/auth/registration/", include("dj_rest_auth.registration.urls")),
    path("api/v1/auth/social/", include("allauth.socialaccount.urls")),
    path("api/v1/accounts/", include("accounts.urls")),
    path("api/v1/users/", include("users.urls")),
    path("api/v1/", include("restaurants.urls")),
    #    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    #    path("swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("", include("web.urls", namespace="web")),
]
