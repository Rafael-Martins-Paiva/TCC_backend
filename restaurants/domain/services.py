import uuid
from django.urls import reverse

class RestaurantURLService:
    def get_public_url(self, restaurant_id: uuid.UUID, base_url: str) -> str:
        path = reverse('web:restaurant_detail', kwargs={'pk': restaurant_id})
        return f"{base_url.rstrip('/')}{path}"
