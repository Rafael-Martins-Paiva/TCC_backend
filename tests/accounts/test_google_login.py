
from django.urls import reverse
from rest_framework.test import APITestCase
from unittest.mock import patch, MagicMock
from django.contrib.auth import get_user_model

User = get_user_model()

class GoogleLoginCallbackViewTest(APITestCase):
    def setUp(self):
        self.google_login_url = reverse('google_login')

    @patch('accounts.views.id_token.verify_oauth2_token')
    def test_google_login_success_existing_user(self, mock_verify_oauth2_token):
        # Mock a chamada para a API do Google
        mock_verify_oauth2_token.return_value = {
            'email': 'test@example.com',
            'name': 'Test User'
        }

        # Cria um usuário existente
        User.objects.create_user(email='test@example.com', password='somepassword', name='Test User', is_verified=True)

        # Chama a view
        response = self.client.post(self.google_login_url, {'id_token': 'fake_token'}, format='json')

        # Verifica a resposta
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['email'], 'test@example.com')

    @patch('accounts.views.id_token.verify_oauth2_token')
    def test_google_login_success_new_user(self, mock_verify_oauth2_token):
        # Mock a chamada para a API do Google
        mock_verify_oauth2_token.return_value = {
            'email': 'newuser@example.com',
            'name': 'New User'
        }

        # Chama a view
        response = self.client.post(self.google_login_url, {'id_token': 'fake_token'}, format='json')

        # Verifica a resposta
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['email'], 'newuser@example.com')

        # Verifica se o usuário foi criado
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())

    def test_google_login_no_token(self):
        # Chama a view sem o token
        response = self.client.post(self.google_login_url, {}, format='json')

        # Verifica a resposta
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'ID token is required.')

    @patch('accounts.views.id_token.verify_oauth2_token')
    def test_google_login_invalid_token(self, mock_verify_oauth2_token):
        # Mock a chamada para a API do Google para retornar um erro
        mock_verify_oauth2_token.side_effect = ValueError('Invalid token')

        # Chama a view
        response = self.client.post(self.google_login_url, {'id_token': 'invalid_token'}, format='json')

        # Verifica a resposta
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'Invalid token: Invalid token')
