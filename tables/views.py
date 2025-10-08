from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.urls import reverse
from .models import Table
from .serializers import TableSerializer
from rest_framework.exceptions import ValidationError # Add this import


class TableViewSet(viewsets.ModelViewSet):
    queryset = Table.objects.all()
    serializer_class = TableSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Table.objects.none()
        try:
            # Ensure the user owns at least one restaurant before filtering
            if not self.request.user.restaurants.exists():
                return Table.objects.none()
            return Table.objects.filter(restaurant__owner=self.request.user)
        except AttributeError:
            # This can happen if 'restaurants' is not a related manager
            # or if the user object doesn't have it for some reason.
            return Table.objects.none()
        except Exception as e:
            # Catch any other unexpected errors during queryset retrieval
            print(f"Error in get_queryset: {e}") # Log the error for debugging
            return Table.objects.none()

    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            raise ValidationError("Authentication required to create a table.")

        restaurant = self.request.user.restaurants.first()
        if not restaurant:
            raise ValidationError("User must own at least one restaurant to create a table.")

        table = serializer.save(restaurant=restaurant)
        qr_code_path = reverse('qr_code_image', kwargs={'data': table.id})
        table.qr_code_url = self.request.build_absolute_uri(qr_code_path)
        table.save()

    @action(detail=True, methods=['patch'])
    def set_status(self, request, pk=None):
        table = self.get_object()
        new_status = request.data.get('status')
        if new_status in [choice[0] for choice in Table.TABLE_STATUS_CHOICES]:
            table.status = new_status
            table.save()
            return Response(TableSerializer(table).data)
        return Response({'status': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)