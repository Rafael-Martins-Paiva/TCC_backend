from accounts.views import CustomTokenObtainPairView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)

from core.qr_codes import qr_code_view # Add this import

"""from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)"""

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/auth/", include("dj_rest_auth.urls")),
    path("api/v1/auth/registration/", include("dj_rest_auth.registration.urls")),
    
    path("api/v1/auth/registration/", include("dj_rest_auth.registration.urls")),
    path("api/v1/accounts/", include("accounts.urls")),
    path("accounts/", include("allauth.urls")),
    path("api/v1/users/", include("users.urls")),
    path("api/v1/", include("restaurants.urls")),
    path("api/v1/", include("orders.urls")),
    path("api/v1/", include("tables.urls")),
    path("api/v1/token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/v1/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/v1/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    #    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    #    path("swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("qr-code/<uuid:data>/", qr_code_view, name="qr_code_image"), # New path
    path("", include("web.urls", namespace="web")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
