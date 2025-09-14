import uuid

from django.conf import settings
from django.db import models


class Restaurant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="restaurants")
    website_content = models.TextField(blank=True, default="")

    def __str__(self):
        return self.name
