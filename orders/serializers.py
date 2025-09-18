from rest_framework import serializers

from restaurants.models import MenuItem, Restaurant
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    menu_item_name = serializers.CharField(source='menu_item.name', read_only=True)
    menu_item_price = serializers.DecimalField(source='menu_item.price', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'menu_item', 'menu_item_name', 'menu_item_price', 'quantity', 'price_at_order']
        read_only_fields = ['id', 'price_at_order']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    user = serializers.StringRelatedField(read_only=True) # Display user's __str__ representation
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'restaurant', 'restaurant_name', 'status', 'created_at', 'updated_at', 'total_price', 'items']
        read_only_fields = ['id', 'status', 'created_at', 'updated_at', 'total_price']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        restaurant = validated_data['restaurant']

        # Ensure the user is the current user
        validated_data['user'] = self.context['request'].user

        order = Order.objects.create(**validated_data)
        total_price = 0

        for item_data in items_data:
            menu_item = item_data['menu_item']
            quantity = item_data['quantity']

            # Validate that the menu item belongs to the specified restaurant
            if menu_item.restaurant != restaurant:
                raise serializers.ValidationError(f"Menu item {menu_item.name} does not belong to restaurant {restaurant.name}.")

            # Store the price at the time of order
            price_at_order = menu_item.price
            OrderItem.objects.create(order=order, menu_item=menu_item, quantity=quantity, price_at_order=price_at_order)
            total_price += (price_at_order * quantity)

        order.total_price = total_price
        order.save()
        return order

    def update(self, instance, validated_data):
        # For now, only status can be updated by restaurant owners
        if 'status' in validated_data:
            instance.status = validated_data.get('status', instance.status)
            instance.save()
        return instance


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']
        read_only_fields = ['id', 'user', 'restaurant', 'created_at', 'updated_at', 'total_price']
