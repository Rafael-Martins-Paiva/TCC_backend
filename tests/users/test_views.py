from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch

User = get_user_model()

class UserMeViewTest(APITestCase):

    def setUp(self):
        self.user_me_url = reverse('user-me')
        self.user = User.objects.create_user(
            email='authenticated@example.com',
            password='TestPass123',
            first_name='Auth',
            last_name='User'
        )

    def get_auth_token(self):
        # Helper to get a JWT token for authentication
        response = self.client.post(reverse('token_obtain_pair'), {
            'email': 'authenticated@example.com',
            'password': 'TestPass123'
        }, format='json')
        self.assertEqual(response.status_code, 200)
        return response.data['access']

    def test_get_user_me_authenticated(self):
        """Test retrieving authenticated user's data."""
        token = self.get_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        response = self.client.get(self.user_me_url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['email'], self.user.email)
        self.assertEqual(response.data['first_name'], self.user.first_name)

    def test_get_user_me_unauthenticated(self):
        """Test retrieving user data without authentication."""
        response = self.client.get(self.user_me_url, format='json')
        self.assertEqual(response.status_code, 401)

    @patch('accounts.services.UserApplicationService.update_user_info')
    def test_patch_user_me_authenticated(self, mock_update_user_info):
        """Test updating authenticated user's data."""
        token = self.get_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        updated_data = {'first_name': 'UpdatedFirst'}
        # Mock the return value of the service method
        self.user.first_name = 'UpdatedFirst'
        mock_update_user_info.return_value = self.user

        response = self.client.patch(self.user_me_url, updated_data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['first_name'], 'UpdatedFirst')
        mock_update_user_info.assert_called_once_with(user_id=self.user.id, data=updated_data)

    def test_patch_user_me_unauthenticated(self):
        """Test updating user data without authentication."""
        updated_data = {'first_name': 'UpdatedFirst'}
        response = self.client.patch(self.user_me_url, updated_data, format='json')
        self.assertEqual(response.status_code, 401)

    def test_patch_user_me_invalid_data(self):
        """Test updating user data with invalid input (e.g., too long first_name)."""
        token = self.get_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        invalid_data = {'first_name': 'a' * 151} # Max length for first_name is 150
        response = self.client.patch(self.user_me_url, invalid_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('first_name', response.data)

    def test_patch_user_me_unallowed_field(self):
        """Test attempting to update a field not allowed by the serializer (e.g., email)."""
        token = self.get_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        unallowed_data = {'email': 'new_email@example.com'}
        response = self.client.patch(self.user_me_url, unallowed_data, format='json')
        self.assertEqual(response.status_code, 400) # DRF returns 400 for unallowed fields
        self.assertIn('email', response.data)

    def test_patch_user_me_empty_data(self):
        """Test sending an empty PATCH request."""
        token = self.get_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        response = self.client.patch(self.user_me_url, {}, format='json')
        self.assertEqual(response.status_code, 200) # Empty patch is valid, no change
