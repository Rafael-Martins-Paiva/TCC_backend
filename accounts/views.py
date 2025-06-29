from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError
from .serializers import UserRegistrationSerializer
from .repositories import DjangoUserRepository
from domain.accounts.services import RegistrationService, UserAlreadyExistsError
from domain.accounts.value_objects.email import InvalidEmailError
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
                first_name=data['first_name'],
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
