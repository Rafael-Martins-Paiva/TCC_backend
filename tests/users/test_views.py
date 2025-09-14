from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

User = get_user_model()


class UserMeViewTest(APITestCase):

    def setUp(self):
        self.user_me_url = reverse("user-me")
        self.user = User.objects.create_user(
            email="authenticated@example.com", password="TestPass123", name="Auth User"
        )

    def tearDown(self):
        pass

    def get_auth_token(self):
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"email": "authenticated@example.com", "password": "TestPass123"},
            format="json",
        )
        print(response.data)
        self.assertEqual(response.status_code, 200)
        return response.data["access"]

    def test_get_user_me_authenticated(self):
        token = self.get_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)

        response = self.client.get(self.user_me_url, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["email"], self.user.email)
        self.assertEqual(response.data["name"], self.user.name)

    def test_get_user_me_unauthenticated(self):
        response = self.client.get(self.user_me_url, format="json")
        self.assertEqual(response.status_code, 401)

    @patch("accounts.services.UserApplicationService.update_user_info")
    def test_patch_user_me_authenticated(self, mock_update_user_info):
        token = self.get_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)

        updated_data = {"name": "UpdatedName"}
        self.user.name = "UpdatedName"
        mock_update_user_info.return_value = self.user

        response = self.client.patch(self.user_me_url, updated_data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "UpdatedName")
        mock_update_user_info.assert_called_once_with(user_id=self.user.id, data=updated_data)

    def test_patch_user_me_unauthenticated(self):
        updated_data = {"first_name": "UpdatedFirst"}
        response = self.client.patch(self.user_me_url, updated_data, format="json")
        self.assertEqual(response.status_code, 401)

    def test_patch_user_me_invalid_data(self):
        token = self.get_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)

        invalid_data = {"name": "a" * 256}
        response = self.client.patch(self.user_me_url, invalid_data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("name", response.data)

    def test_patch_user_me_unallowed_field(self):
        token = self.get_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)

        unallowed_data = {"email": "new_email@example.com"}
        response = self.client.patch(self.user_me_url, unallowed_data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.data)

    def test_patch_user_me_empty_data(self):
        token = self.get_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)

        response = self.client.patch(self.user_me_url, {}, format="json")
        self.assertEqual(response.status_code, 200)
