from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from accounts.serializers import UserSerializer, UserUpdateSerializer
from accounts.services import UserApplicationService

class UserMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retorna os dados do usuário autenticado."""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        """Atualiza dados parciais do usuário autenticado."""
        serializer = UserUpdateSerializer(instance=request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        # Orquestra a atualização através do serviço de aplicação
        user_service = UserApplicationService()
        updated_user = user_service.update_user_info(user_id=request.user.id, data=serializer.validated_data)

        # Retorna os dados atualizados
        response_serializer = UserSerializer(updated_user)
        return Response(response_serializer.data)