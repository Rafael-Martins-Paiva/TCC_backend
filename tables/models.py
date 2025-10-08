import uuid

from django.db import models
from restaurants.models import Restaurant


class Table(models.Model):
    TABLE_STATUS_CHOICES = [
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('reserved', 'Reserved'),
        ('needs_cleaning', 'Needs Cleaning'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='tables')
    table_number = models.CharField(max_length=50, unique=True)
    capacity = models.PositiveSmallIntegerField()
    status = models.CharField(max_length=20, choices=TABLE_STATUS_CHOICES, default='available')
    qr_code_url = models.URLField(max_length=200, blank=True, null=True)

    class Meta:
        unique_together = ('restaurant', 'table_number')
        ordering = ['table_number']

    def __str__(self):
        return f"Table {self.table_number} ({self.restaurant.name})"