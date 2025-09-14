from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import User
from restaurants.models import Restaurant


class RestaurantPaginationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email="test@example.com", password="password123")
        # Create 20 restaurants for pagination testing
        for i in range(1, 21):
            Restaurant.objects.create(name=f"Restaurant {i:02d}", owner=self.user)

    def test_first_page_next_pagination(self):
        response = self.client.get(reverse("web:restaurant_list") + "?limit=5")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["has_next"])
        self.assertFalse(response.context["has_previous"])
        self.assertEqual(len(response.context["restaurants"]), 5)
        self.assertEqual(response.context["restaurants"][0].name, "Restaurant 01")
        self.assertEqual(response.context["restaurants"][4].name, "Restaurant 05")
        self.assertEqual(response.context["next_cursor"], "Restaurant 05")

    def test_second_page_next_pagination(self):
        # Get first page's next_cursor
        response_first_page = self.client.get(reverse("web:restaurant_list") + "?limit=5")
        next_cursor = response_first_page.context["next_cursor"]

        response = self.client.get(reverse("web:restaurant_list") + f"?limit=5&cursor={next_cursor}&direction=next")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["has_next"])
        self.assertTrue(response.context["has_previous"])
        self.assertEqual(len(response.context["restaurants"]), 5)
        self.assertEqual(response.context["restaurants"][0].name, "Restaurant 06")
        self.assertEqual(response.context["restaurants"][4].name, "Restaurant 10")
        self.assertEqual(response.context["next_cursor"], "Restaurant 10")
        self.assertEqual(response.context["previous_cursor"], "Restaurant 06")

    def test_previous_pagination(self):
        # Go to second page
        response_first_page = self.client.get(reverse("web:restaurant_list") + "?limit=5")
        next_cursor = response_first_page.context["next_cursor"]
        response_second_page = self.client.get(
            reverse("web:restaurant_list") + f"?limit=5&cursor={next_cursor}&direction=next"
        )
        previous_cursor_from_second_page = response_second_page.context["previous_cursor"]

        # Go back to first page
        response = self.client.get(
            reverse("web:restaurant_list") + f"?limit=5&cursor={previous_cursor_from_second_page}&direction=prev"
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["has_next"])
        self.assertFalse(response.context["has_previous"])
        self.assertEqual(len(response.context["restaurants"]), 5)
        self.assertEqual(response.context["restaurants"][0].name, "Restaurant 01")
        self.assertEqual(response.context["restaurants"][4].name, "Restaurant 05")
        self.assertEqual(response.context["next_cursor"], "Restaurant 05")

    def test_last_page_next_pagination(self):
        # Directly request the last page
        response = self.client.get(reverse("web:restaurant_list") + "?limit=5&cursor=Restaurant 15&direction=next")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["has_next"])
        self.assertTrue(response.context["has_previous"])
        self.assertEqual(len(response.context["restaurants"]), 5)
        self.assertEqual(response.context["restaurants"][0].name, "Restaurant 16")
        self.assertEqual(response.context["restaurants"][4].name, "Restaurant 20")
        self.assertEqual(response.context["previous_cursor"], "Restaurant 16")

    def test_empty_list(self):
        Restaurant.objects.all().delete()  # Clear all restaurants
        response = self.client.get(reverse("web:restaurant_list") + "?limit=5")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["has_next"])
        self.assertFalse(response.context["has_previous"])
        self.assertEqual(len(response.context["restaurants"]), 0)

    def test_single_page(self):
        Restaurant.objects.all().delete()
        Restaurant.objects.create(name="Single Restaurant", owner=self.user)
        response = self.client.get(reverse("web:restaurant_list") + "?limit=5")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["has_next"])
        self.assertFalse(response.context["has_previous"])
        self.assertEqual(len(response.context["restaurants"]), 1)
        self.assertEqual(response.context["restaurants"][0].name, "Single Restaurant")
