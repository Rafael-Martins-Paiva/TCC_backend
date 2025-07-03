from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from .serializers import UserRegistrationSerializer, EmailVerificationSerializer, ResendVerificationEmailSerializer, ChangePasswordSerializer
from .repositories import DjangoUserRepository
from .services import ChangePasswordApplicationService
from domain.accounts.services.registration_service import RegistrationService
from domain.accounts.services.email_verification_service import EmailVerificationService
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
        except UserAlreadyExistsError as e: # This can happen if email is not found
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

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


