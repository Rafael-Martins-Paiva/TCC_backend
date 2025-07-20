from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from .serializers import UserRegistrationSerializer, EmailVerificationSerializer, ResendVerificationEmailSerializer, ChangePasswordSerializer, LogoutSerializer
from .repositories import DjangoUserRepository
from .services import ChangePasswordApplicationService
from domain.accounts.services.registration_service import RegistrationService
from domain.accounts.services.email_verification_service import EmailVerificationService
from domain.accounts.services.logout_service import LogoutService
from domain.accounts.exceptions.auth_exceptions import UserAlreadyExistsError, InvalidVerificationTokenError, InvalidOldPasswordError
from domain.accounts.aggregates.value_objects.email import InvalidEmailError

class UserRegistrationAPIView(generics.GenericAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        user_repo = DjangoUserRepository()
        
        
        registration_service = RegistrationService(user_repository=user_repo)
        try:
            
            registration_service.register_user(
                email=str(data['email']), 
                name=data.get('name', ''),
                password=data['password']
            )
        except UserAlreadyExistsError as e:
            
            return Response({"email": str(e)}, status=status.HTTP_409_CONFLICT)
        except InvalidEmailError as e:
            
            return Response({"email": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {"message": f"Usuário {data['email']} criado com sucesso."},
            status=status.HTTP_201_CREATED
        )

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
            email_verification_service.verify_email(
                email=data['email'],
                token=data['token']
            )
        except InvalidVerificationTokenError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except UserAlreadyExistsError as e: # This exception type seems wrong here, should be UserNotFoundError
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

        return Response({"message": "Email verificado com sucesso."}, status=status.HTTP_200_OK)

    def get(self, request, *args, **kwargs):
        email = request.query_params.get('email')
        token = request.query_params.get('token')

        if not email or not token:
            return Response({"detail": "Email e token são obrigatórios."}, status=status.HTTP_400_BAD_REQUEST)

        user_repo = DjangoUserRepository()
        email_verification_service = EmailVerificationService(user_repository=user_repo)

        try:
            email_verification_service.verify_email(
                email=email,
                token=token
            )
        except InvalidVerificationTokenError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Email verificado com sucesso."}, status=status.HTTP_200_OK)

class ResendVerificationEmailAPIView(generics.GenericAPIView):
    serializer_class = ResendVerificationEmailSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user_repo = DjangoUserRepository()
        email_verification_service = EmailVerificationService(user_repository=user_repo)

        try:
            user = email_verification_service.resend_verification_email(
                email=data['email']
            )
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
        old_password = data['old_password']
        new_password = data['new_password']

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
            result = service.logout(serializer.validated_data['refresh'])
            if 'error' in result:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
            return Response(result, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from django.conf import settings
from google.oauth2 import id_token
from google.auth.transport import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User

class GoogleLoginCallbackView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        token = request.data.get('id_token')
        if not token:
            return Response({'error': 'ID token is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            CLIENT_ID = settings.SOCIALACCOUNT_PROVIDERS['google']['APP']['client_id']
            idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)

            email = idinfo['email']
            name = idinfo.get('name', '')

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                user = User.objects.create_user(email=email, name=name, password=None)
                user.is_verified = True
                user.save()

            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'name': user.name,
                }
            })

        except ValueError as e:
            return Response({'error': f'Invalid token: {e}'}, status=status.HTTP_400_BAD_REQUEST)