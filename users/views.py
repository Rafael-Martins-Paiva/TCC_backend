from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.serializers import UserSerializer, UserUpdateSerializer
from accounts.services import UserApplicationService


class UserMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserUpdateSerializer(instance=request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        user_service = UserApplicationService()
        updated_user = user_service.update_user_info(user_id=request.user.id, data=serializer.validated_data)

        response_serializer = UserSerializer(updated_user)
        return Response(response_serializer.data)
