from rest_framework import serializers

from .models import Restaurant


class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ["id", "name", "owner"]
        read_only_fields = ["id", "owner"]


class RestaurantContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ["website_content"]
