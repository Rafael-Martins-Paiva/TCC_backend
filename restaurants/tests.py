from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import MenuItem, Restaurant

User = get_user_model()


class MenuItemAPITests(APITestCase):
    def setUp(self):
        # Create two users
        self.owner1 = User.objects.create_user(email="owner1@example.com", password="password123", has_paid_plan=True)
        self.owner2 = User.objects.create_user(email="owner2@example.com", password="password123", has_paid_plan=True)

        # Create two restaurants
        self.restaurant1 = Restaurant.objects.create(name="Restaurant 1", owner=self.owner1)
        self.restaurant2 = Restaurant.objects.create(name="Restaurant 2", owner=self.owner2)

        # Create a menu item for restaurant 1
        self.menu_item1 = MenuItem.objects.create(restaurant=self.restaurant1, name="Pizza", price=12.99)

    def test_list_menu_items(self):
        """Ensure any user can list menu items for a restaurant."""
        url = reverse("menu-item-list-create", kwargs={"restaurant_pk": self.restaurant1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Pizza")

    def test_create_menu_item_unauthenticated(self):
        """Ensure unauthenticated user cannot create a menu item."""
        url = reverse("menu-item-list-create", kwargs={"restaurant_pk": self.restaurant1.pk})
        data = {"name": "Burger", "price": 9.99}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_menu_item_by_owner(self):
        """Ensure the restaurant owner can create a menu item."""
        url = reverse("menu-item-list-create", kwargs={"restaurant_pk": self.restaurant1.pk})
        data = {"name": "Burger", "price": 9.99}
        self.client.force_authenticate(user=self.owner1)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.restaurant1.menu_items.count(), 2)

    def test_create_menu_item_by_non_owner(self):
        """Ensure a non-owner cannot create a menu item."""
        url = reverse("menu-item-list-create", kwargs={"restaurant_pk": self.restaurant1.pk})
        data = {"name": "Burger", "price": 9.99}
        self.client.force_authenticate(user=self.owner2)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_menu_item_by_owner(self):
        """Ensure the restaurant owner can update a menu item."""
        url = reverse(
            "menu-item-detail", kwargs={"restaurant_pk": self.restaurant1.pk, "menu_item_pk": self.menu_item1.pk}
        )
        data = {"price": 15.99}
        self.client.force_authenticate(user=self.owner1)
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.menu_item1.refresh_from_db()
        self.assertEqual(self.menu_item1.price, Decimal("15.99"))

    def test_update_menu_item_by_non_owner(self):
        """Ensure a non-owner cannot update a menu item."""
        url = reverse(
            "menu-item-detail", kwargs={"restaurant_pk": self.restaurant1.pk, "menu_item_pk": self.menu_item1.pk}
        )
        data = {"price": 15.99}
        self.client.force_authenticate(user=self.owner2)
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_menu_item_by_owner(self):
        """Ensure the restaurant owner can delete a menu item."""
        url = reverse(
            "menu-item-detail", kwargs={"restaurant_pk": self.restaurant1.pk, "menu_item_pk": self.menu_item1.pk}
        )
        self.client.force_authenticate(user=self.owner1)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.restaurant1.menu_items.count(), 0)

    def test_delete_menu_item_by_non_owner(self):
        """Ensure a non-owner cannot delete a menu item."""
        url = reverse(
            "menu-item-detail", kwargs={"restaurant_pk": self.restaurant1.pk, "menu_item_pk": self.menu_item1.pk}
        )
        self.client.force_authenticate(user=self.owner2)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
