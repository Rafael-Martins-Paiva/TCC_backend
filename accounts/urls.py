from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from .views import (
    ChangePasswordAPIView,
    CustomTokenObtainPairView,
    EmailVerificationAPIView,
    GoogleLoginCallbackView,
    LogoutView,
    ResendVerificationEmailAPIView,
    UserRegistrationAPIView,
)

urlpatterns = [
    path("register/", UserRegistrationAPIView.as_view(), name="user-register"),
    path("verify-email/", EmailVerificationAPIView.as_view(), name="verify-email"),
    path("resend-verification-email/", ResendVerificationEmailAPIView.as_view(), name="resend-verification-email"),
    path("change-password/", ChangePasswordAPIView.as_view(), name="change-password"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("google/login/", GoogleLoginCallbackView.as_view(), name="google_login"),
]
