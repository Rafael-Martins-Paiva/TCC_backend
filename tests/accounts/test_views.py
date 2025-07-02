from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch

User = get_user_model()

class UserRegistrationAPITest(APITestCase):

    def setUp(self):
        self.register_url = reverse('user-register')
        self.user_data = {
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'StrongPassword123',
            'password2': 'StrongPassword123'
        }

    @patch('accounts.views.RegistrationService.register_user')
    def test_user_registration_success(self, mock_register_user):
        """Test successful user registration."""
        mock_register_user.return_value = None # Simulate successful registration

        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('message', response.data)
        self.assertIn('Usuário test@example.com criado com sucesso.', response.data['message'])
        mock_register_user.assert_called_once()

    @patch('accounts.views.RegistrationService.register_user')
    def test_user_registration_existing_email(self, mock_register_user):
        """Test registration with an email that already exists."""
        from domain.accounts.services.auth_service import UserAlreadyExistsError
        mock_register_user.side_effect = UserAlreadyExistsError("User with this email already exists.")

        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, 409)
        self.assertIn('email', response.data)
        self.assertEqual(response.data['email'], "User with this email already exists.")
        mock_register_user.assert_called_once()

    def test_user_registration_invalid_email(self):
        """Test registration with an invalid email format."""
        invalid_email_data = self.user_data.copy()
        invalid_email_data['email'] = 'invalid-email'
        response = self.client.post(self.register_url, invalid_email_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('email', response.data)
        self.assertEqual(response.data['email'][0], 'Endereço de e-mail inválido: invalid-email')

    def test_user_registration_missing_required_fields(self):
        """Test registration with missing required fields."""
        # Missing email
        missing_email_data = self.user_data.copy()
        missing_email_data.pop('email')
        response = self.client.post(self.register_url, missing_email_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('email', response.data)

        # Missing password
        missing_password_data = self.user_data.copy()
        missing_password_data.pop('password')
        response = self.client.post(self.register_url, missing_password_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('password', response.data)

        # Missing password2
        missing_password2_data = self.user_data.copy()
        missing_password2_data.pop('password2')
        response = self.client.post(self.register_url, missing_password2_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('password2', response.data)

    def test_user_registration_password_mismatch(self):
        """Test registration with mismatched passwords."""
        mismatched_password_data = self.user_data.copy()
        mismatched_password_data['password2'] = 'DifferentPassword123'
        response = self.client.post(self.register_url, mismatched_password_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('password', response.data)
        self.assertEqual(response.data['password'][0], 'As senhas não coincidem.')

    def test_user_registration_optional_fields(self):
        """Test registration without optional fields (first_name, last_name)."""
        data_without_optional = {
            'email': 'no_optional@example.com',
            'password': 'StrongPassword123',
            'password2': 'StrongPassword123'
        }
        with patch('accounts.views.RegistrationService.register_user') as mock_register_user:
            mock_register_user.return_value = None
            response = self.client.post(self.register_url, data_without_optional, format='json')
            self.assertEqual(response.status_code, 201)
            mock_register_user.assert_called_once_with(
                email='no_optional@example.com',
                first_name='', # Should be empty string if not provided
                last_name='',  # Should be empty string if not provided
                password='StrongPassword123'
            )


