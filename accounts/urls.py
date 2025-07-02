from django.urls import path
from .views import UserRegistrationAPIView, EmailVerificationAPIView, ResendVerificationEmailAPIView, ChangePasswordAPIView

urlpatterns = [
    path('register/', UserRegistrationAPIView.as_view(), name='user-register'),
    path('verify-email/', EmailVerificationAPIView.as_view(), name='verify-email'),
    path('resend-verification-email/', ResendVerificationEmailAPIView.as_view(), name='resend-verification-email'),
    path('change-password/', ChangePasswordAPIView.as_view(), name='change-password'),
    
]
