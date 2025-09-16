from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from restaurants.models import Restaurant

User = get_user_model()


class RestaurantAPITests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(email="test@example.com", password="password123", has_paid_plan=True)
        self.other_user = User.objects.create_user(
            email="other@example.com", password="password123", has_paid_plan=True
        )
        self.client.force_authenticate(user=self.user)
        self.restaurant = Restaurant.objects.create(name="Test Restaurant", owner=self.user)

    def test_create_restaurant_without_paid_plan(self):
        unpaid_user = User.objects.create_user(email="unpaid@example.com", password="password123", has_paid_plan=False)
        self.client.force_authenticate(user=unpaid_user)
        url = reverse("restaurant-create")
        data = {"name": "Free Restaurant"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Restaurant.objects.count(), 1)  # Should not create a new restaurant

    def test_create_restaurant(self):
        url = reverse("restaurant-create")
        data = {"name": "New Restaurant"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Restaurant.objects.count(), 2)
        new_restaurant = Restaurant.objects.get(name="New Restaurant")
        self.assertEqual(new_restaurant.owner, self.user)

    def test_update_restaurant_content_by_owner(self):
        url = reverse("restaurant-content-update", kwargs={"pk": self.restaurant.pk})
        data = {"website_content": '<p>Hello</p><script>alert("xss")</script>'}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.restaurant.refresh_from_db()
        self.assertEqual(self.restaurant.website_content, '<p>Hello</p><script>alert("xss")</script>')

    def test_update_restaurant_content_by_non_owner(self):
        self.client.force_authenticate(user=self.other_user)
        url = reverse("restaurant-content-update", kwargs={"pk": self.restaurant.pk})
        data = {"website_content": "<p>Hello</p>"}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_all_restaurants(self):
        url = reverse("restaurant-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only the one created in setUp

    def test_list_my_restaurants(self):
        # Create another restaurant for the other user
        Restaurant.objects.create(name="Other User Restaurant", owner=self.other_user)

        url = reverse("my-restaurant-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only the one owned by self.user
        self.assertEqual(response.data[0]["name"], "Test Restaurant")

    def test_delete_restaurant_by_owner(self):
        url = reverse("restaurant-detail", kwargs={"pk": self.restaurant.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Restaurant.objects.count(), 0)

    def test_delete_restaurant_by_non_owner(self):
        self.client.force_authenticate(user=self.other_user)
        url = reverse("restaurant-detail", kwargs={"pk": self.restaurant.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Restaurant.objects.count(), 1)  # Should not be deleted

    def test_view_restaurant_website(self):
        # Make the content available
        self.restaurant.website_content = "<h1>Welcome</h1>"
        self.restaurant.save()

        # Unauthenticated client should be able to view
        self.client.logout()

        url = reverse("restaurant-content-view", kwargs={"pk": self.restaurant.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content.decode(), "<h1>Welcome</h1>")
        self.assertEqual(response["Content-Type"], "text/html")
