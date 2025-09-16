from rest_framework import serializers

from .models import InventoryItem, MenuItem, Restaurant, Review


class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ["id", "name", "owner"]
        read_only_fields = ["id", "owner"]


class RestaurantContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ["website_content"]


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = [
            "id",
            "name",
            "description",
            "price",
            "is_available",
            "restaurant",
            "ingredients",
            "allergens",
        ]
        read_only_fields = ["id", "restaurant"]


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Review
        fields = ["id", "author", "rating", "comment", "restaurant", "menu_item", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate(self, data):
        restaurant = data.get("restaurant")
        menu_item = data.get("menu_item")

        if not restaurant and not menu_item:
            raise serializers.ValidationError("Either 'restaurant' or 'menu_item' must be provided.")
        if restaurant and menu_item:
            raise serializers.ValidationError("Cannot provide both 'restaurant' and 'menu_item'.")

        return data


class InventoryItemSerializer(serializers.ModelSerializer):
    menu_item_name = serializers.CharField(source="menu_item.name", read_only=True)

    class Meta:
        model = InventoryItem
        fields = ["id", "menu_item", "menu_item_name", "quantity", "last_updated"]
        read_only_fields = ["id", "menu_item", "menu_item_name", "last_updated"]
