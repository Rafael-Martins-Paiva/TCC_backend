from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from accounts.views import UserMeView # Import UserMeView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('api/v1/accounts/', include('accounts.urls')),
    path('api/v1/users/me/', UserMeView.as_view(), name='user-me'), # New path for users/me
    
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
