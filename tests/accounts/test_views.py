from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class UserRegistrationAPITest(APITestCase):

    def setUp(self):
        self.register_url = reverse('user-register')
        self.logout_url = reverse('logout')
        self.user = User.objects.create_user(email='test@example.com', password='password123')
        self.refresh_token = RefreshToken.for_user(self.user)
        self.user_data = {
            'email': 'test@example.com',
            'name': 'Test User',
            'password': 'StrongPassword123',
            'password2': 'StrongPassword123'
        }

    @patch('accounts.views.LogoutService.logout')
    def test_logout_success(self, mock_logout):
        mock_logout.return_value = {"success": "User logged out successfully."}
        response = self.client.post(self.logout_url, {'refresh': str(self.refresh_token)}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('success', response.data)
        mock_logout.assert_called_once_with(str(self.refresh_token))

    @patch('accounts.views.RegistrationService.register_user')
    def test_user_registration_success(self, mock_register_user):
        mock_register_user.return_value = None 

        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('message', response.data)
        self.assertIn('Usuário test@example.com criado com sucesso.', response.data['message'])
        mock_register_user.assert_called_once()

    @patch('accounts.views.RegistrationService.register_user')
    def test_user_registration_existing_email(self, mock_register_user):
        from domain.accounts.exceptions.auth_exceptions import UserAlreadyExistsError
        mock_register_user.side_effect = UserAlreadyExistsError("User with this email already exists.")

        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, 409)
        self.assertIn('email', response.data)
        self.assertEqual(response.data['email'], "User with this email already exists.")
        mock_register_user.assert_called_once()

    def test_user_registration_invalid_email(self):
        invalid_email_data = self.user_data.copy()
        invalid_email_data['email'] = 'invalid-email'
        response = self.client.post(self.register_url, invalid_email_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('email', response.data)
        self.assertEqual(response.data['email'][0], 'Endereço de e-mail inválido: invalid-email')

    def test_user_registration_missing_required_fields(self):
        missing_email_data = self.user_data.copy()
        missing_email_data.pop('email')
        response = self.client.post(self.register_url, missing_email_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('email', response.data)

        missing_password_data = self.user_data.copy()
        missing_password_data['email'] = 'another@example.com'
        missing_password_data.pop('password')
        response = self.client.post(self.register_url, missing_password_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('password', response.data)

        missing_password2_data = self.user_data.copy()
        missing_password2_data['email'] = 'another2@example.com'
        missing_password2_data.pop('password2')
        response = self.client.post(self.register_url, missing_password2_data, format='json')
        self.assertEqual(response.status_code, 201)

    def test_user_registration_password_mismatch(self):
        mismatched_password_data = self.user_data.copy()
        mismatched_password_data['password2'] = 'DifferentPassword123'
        response = self.client.post(self.register_url, mismatched_password_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('password', response.data)
        self.assertEqual(response.data['password'][0], 'As senhas não coincidem.')

    def test_user_registration_optional_fields(self):
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
                name='', 
                password='StrongPassword123'
            )


