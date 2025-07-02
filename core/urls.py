from django.contrib import admin
from django.urls import path, include
"""from drf_spectacular.views import (
    SpectacularAPIView, 
    SpectacularSwaggerView,
)"""
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('api/v1/accounts/', include('accounts.urls')),
    path('api/v1/users/', include('users.urls')),
#    path("schema/", SpectacularAPIView.as_view(), name="schema"),
#    path("swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
