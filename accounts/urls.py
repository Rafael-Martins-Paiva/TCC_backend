from django.urls import path
from .views import UserRegistrationAPIView, EmailVerificationAPIView, ResendVerificationEmailAPIView, ChangePasswordAPIView, LogoutView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('register/', UserRegistrationAPIView.as_view(), name='user-register'),
    path('verify-email/', EmailVerificationAPIView.as_view(), name='verify-email'),
    path('resend-verification-email/', ResendVerificationEmailAPIView.as_view(), name='resend-verification-email'),
    path('change-password/', ChangePasswordAPIView.as_view(), name='change-password'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
