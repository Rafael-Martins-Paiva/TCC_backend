from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from restaurants.models import InventoryItem, MenuItem, Restaurant

User = get_user_model()


class InventoryAPITests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(email="test@example.com", password="password123", has_paid_plan=True)
        self.other_user = User.objects.create_user(
            email="other@example.com", password="password123", has_paid_plan=True
        )
        self.client.force_authenticate(user=self.user)
        self.restaurant = Restaurant.objects.create(name="Test Restaurant", owner=self.user)
        self.menu_item = MenuItem.objects.create(restaurant=self.restaurant, name="Burger", price=10.00)
        self.inventory_item = InventoryItem.objects.create(menu_item=self.menu_item, quantity=50)

        self.restaurant_other = Restaurant.objects.create(name="Other Restaurant", owner=self.other_user)
        self.menu_item_other = MenuItem.objects.create(restaurant=self.restaurant_other, name="Pizza", price=15.00)
        self.inventory_item_other = InventoryItem.objects.create(menu_item=self.menu_item_other, quantity=30)

    def test_list_inventory_items_authenticated(self):
        url = reverse("inventory-item-list-create", kwargs={"restaurant_pk": self.restaurant.pk})
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["menu_item_name"], self.menu_item.name)

    def test_list_inventory_items_unauthenticated(self):
        self.client.logout()
        url = reverse("inventory-item-list-create", kwargs={"restaurant_pk": self.restaurant.pk})
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_inventory_item_by_owner(self):
        new_menu_item = MenuItem.objects.create(restaurant=self.restaurant, name="Fries", price=5.00)
        url = reverse("inventory-item-list-create", kwargs={"restaurant_pk": self.restaurant.pk})
        data = {"menu_item": new_menu_item.pk, "quantity": 100}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(InventoryItem.objects.count(), 3)
        self.assertTrue(InventoryItem.objects.filter(menu_item=new_menu_item).exists())

    def test_create_inventory_item_by_non_owner(self):
        new_menu_item = MenuItem.objects.create(restaurant=self.restaurant, name="Salad", price=8.00)
        self.client.force_authenticate(user=self.other_user)
        url = reverse("inventory-item-list-create", kwargs={"restaurant_pk": self.restaurant.pk})
        data = {"menu_item": new_menu_item.pk, "quantity": 75}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(InventoryItem.objects.count(), 2)  # Should not create

    def test_create_inventory_item_already_exists(self):
        url = reverse("inventory-item-list-create", kwargs={"restaurant_pk": self.restaurant.pk})
        data = {"menu_item": self.menu_item.pk, "quantity": 20}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Inventory item already exists for this menu item.", str(response.data))

    def test_retrieve_inventory_item_by_owner(self):
        url = reverse(
            "inventory-item-detail", kwargs={"restaurant_pk": self.restaurant.pk, "menu_item_pk": self.menu_item.pk}
        )
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["quantity"], 50)

    def test_retrieve_inventory_item_by_non_owner(self):
        self.client.force_authenticate(user=self.other_user)
        url = reverse(
            "inventory-item-detail", kwargs={"restaurant_pk": self.restaurant.pk, "menu_item_pk": self.menu_item.pk}
        )
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_inventory_item_unauthenticated(self):
        self.client.logout()
        self.client.credentials()  # Ensure no authentication headers are sent
        url = reverse(
            "inventory-item-detail", kwargs={"restaurant_pk": self.restaurant.pk, "menu_item_pk": self.menu_item.pk}
        )
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_inventory_item_by_owner(self):
        url = reverse(
            "inventory-item-detail", kwargs={"restaurant_pk": self.restaurant.pk, "menu_item_pk": self.menu_item.pk}
        )
        data = {"quantity": 75}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.inventory_item.refresh_from_db()
        self.assertEqual(self.inventory_item.quantity, 75)

    def test_update_inventory_item_by_non_owner(self):
        self.client.force_authenticate(user=self.other_user)
        url = reverse(
            "inventory-item-detail", kwargs={"restaurant_pk": self.restaurant.pk, "menu_item_pk": self.menu_item.pk}
        )
        data = {"quantity": 60}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.inventory_item.refresh_from_db()
        self.assertEqual(self.inventory_item.quantity, 50)  # Should not be updated

    def test_update_inventory_item_with_invalid_quantity(self):
        url = reverse(
            "inventory-item-detail", kwargs={"restaurant_pk": self.restaurant.pk, "menu_item_pk": self.menu_item.pk}
        )
        data = {"quantity": -10}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Ensure this value is greater than or equal to 0.", str(response.data))
        self.inventory_item.refresh_from_db()
        self.assertEqual(self.inventory_item.quantity, 50)  # Should not be updated
