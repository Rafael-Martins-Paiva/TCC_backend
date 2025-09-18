from accounts.views import CustomTokenObtainPairView
from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)

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
    path("api/v1/", include("orders.urls")),
    path("api/v1/token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/v1/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/v1/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    #    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    #    path("swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("", include("web.urls", namespace="web")),
]
