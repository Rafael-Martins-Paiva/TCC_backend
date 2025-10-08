import uuid

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import CheckConstraint, Q


class Restaurant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="restaurants")
    website_content = models.TextField(blank=True, default="")

    def __str__(self):
        return self.name

    def get_inventory_items(self):
        return InventoryItem.objects.filter(menu_item__restaurant=self)


class MenuItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="menu_items")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)
    ingredients = models.JSONField(default=list, blank=True, help_text="List of ingredients.")
    allergens = models.JSONField(default=list, blank=True, help_text="List of allergens.")
    cover = models.ImageField(
        upload_to="menu_items/covers/", blank=True, null=True, help_text="Cover image for the menu item."
    )

    class Meta:
        ordering = ["name"]
        unique_together = ("restaurant", "name")

    def __str__(self):
        return f"{self.name} - {self.restaurant.name}"

    def get_unavailable_ingredients(self):
        """
        Checks the ingredients list against StockItem for availability.
        Returns a list of ingredient names that are out of stock.
        """
        if not self.ingredients:
            return []

        # The ingredients field is now a list of strings
        ingredient_names = self.ingredients

        # Find stock items for this restaurant that match the ingredient names and are out of stock
        out_of_stock_items = StockItem.objects.filter(
            restaurant=self.restaurant, name__in=ingredient_names, quantity=0
        ).values_list("name", flat=True)

        return list(out_of_stock_items)


class MenuItemMedia(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name="media")
    file = models.FileField(upload_to="menu_items/media/")

    MEDIA_TYPE_CHOICES = [
        ("image", "Image"),
        ("video", "Video"),
    ]
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.media_type} for {self.menu_item.name}"


class Review(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="reviews", null=True, blank=True)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name="reviews", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            CheckConstraint(
                check=Q(restaurant__isnull=False, menu_item__isnull=True)
                | Q(restaurant__isnull=True, menu_item__isnull=False),
                name="review_target_is_exclusive",
            )
        ]

    def __str__(self):
        target = self.restaurant or self.menu_item
        return f"Review by {self.author.get_username()} for {target}"


class InventoryItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    menu_item = models.OneToOneField(MenuItem, on_delete=models.CASCADE, related_name="inventory")
    quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Inventory Item"
        verbose_name_plural = "Inventory Items"

    def __str__(self):
        return f"Inventory for {self.menu_item.name}: {self.quantity}"


class StockItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="stock_items")
    name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("restaurant", "name")
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.quantity}) for {self.restaurant.name}"
