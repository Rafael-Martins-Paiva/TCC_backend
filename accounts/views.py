from django.conf import settings
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from core.decorators import rate_limit
from domain.accounts.aggregates.value_objects.email import InvalidEmailError
from domain.accounts.exceptions.auth_exceptions import (
    InvalidOldPasswordError,
    InvalidVerificationTokenError,
    UserAlreadyExistsError,
)
from domain.accounts.services.email_verification_service import EmailVerificationService
from domain.accounts.services.logout_service import LogoutService
from domain.accounts.services.registration_service import RegistrationService

from .models import User
from .repositories import DjangoUserRepository
from .serializers import (
    ChangePasswordSerializer,
    CustomLoginSerializer,
    EmailVerificationSerializer,
    LogoutSerializer,
    ResendVerificationEmailSerializer,
    UserRegistrationSerializer,
)
from .services import ChangePasswordApplicationService


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomLoginSerializer


class UserRegistrationAPIView(generics.GenericAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    @rate_limit(max_calls=5, window=300)  # Limita a 5 registros a cada 5 minutos
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user_repo = DjangoUserRepository()

        registration_service = RegistrationService(user_repository=user_repo)
        try:

            registration_service.register_user(
                email=str(data["email"]), name=data.get("name", ""), password=data["password"]
            )
        except UserAlreadyExistsError as e:

            return Response({"email": str(e)}, status=status.HTTP_409_CONFLICT)
        except InvalidEmailError as e:

            return Response({"email": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": f"Usuário {data['email']} criado com sucesso."}, status=status.HTTP_201_CREATED)


class EmailVerificationAPIView(generics.GenericAPIView):
    serializer_class = EmailVerificationSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user_repo = DjangoUserRepository()
        email_verification_service = EmailVerificationService(user_repository=user_repo)

        try:
            email_verification_service.verify_email(email=data["email"], token=data["token"])
        except InvalidVerificationTokenError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except UserAlreadyExistsError as e:  # This exception type seems wrong here, should be UserNotFoundError
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

        return Response({"message": "Email verificado com sucesso."}, status=status.HTTP_200_OK)

    def get(self, request, *args, **kwargs):
        email = request.query_params.get("email")
        token = request.query_params.get("token")

        if not email or not token:
            return Response({"detail": "Email e token são obrigatórios."}, status=status.HTTP_400_BAD_REQUEST)

        user_repo = DjangoUserRepository()
        email_verification_service = EmailVerificationService(user_repository=user_repo)

        try:
            email_verification_service.verify_email(email=email, token=token)
        except InvalidVerificationTokenError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Email verificado com sucesso."}, status=status.HTTP_200_OK)


class ResendVerificationEmailAPIView(generics.GenericAPIView):
    serializer_class = ResendVerificationEmailSerializer
    permission_classes = [AllowAny]

    @rate_limit(max_calls=3, window=600)  # Limita a 3 reenvios a cada 10 minutos
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user_repo = DjangoUserRepository()
        email_verification_service = EmailVerificationService(user_repository=user_repo)

        try:
            email_verification_service.resend_verification_email(email=data["email"])
        except UserAlreadyExistsError as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

        return Response({"message": "Email de verificação reenviado com sucesso."}, status=status.HTTP_200_OK)


class ChangePasswordAPIView(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = request.user
        old_password = data["old_password"]
        new_password = data["new_password"]

        change_password_service = ChangePasswordApplicationService()

        try:
            change_password_service.change_password(user, old_password, new_password)
        except InvalidOldPasswordError as e:
            return Response({"old_password": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Senha alterada com sucesso."}, status=status.HTTP_200_OK)


class LogoutView(APIView):
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        if serializer.is_valid():
            service = LogoutService()
            result = service.logout(serializer.validated_data["refresh"])
            if "error" in result:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
            return Response(result, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





class GetAuthTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        })
