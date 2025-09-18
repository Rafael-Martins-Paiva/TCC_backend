from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

from domain.accounts.aggregates.account import User as UserEntity
from domain.accounts.aggregates.value_objects.email import Email
from domain.accounts.events.user_registered import UserRegistered
from domain.accounts.exceptions.auth_exceptions import (
    InvalidOldPasswordError,
    InvalidVerificationTokenError,
    UserAlreadyExistsError,
)

User = get_user_model()


class AuthFlowsAPITest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="oldpassword",
            name="Test User",
            is_verified=False,
            verification_token="test_token",
        )
        self.verify_email_url = reverse("verify-email")
        self.resend_verification_url = reverse("resend-verification-email")
        self.change_password_url = reverse("change-password")

    @patch("accounts.views.EmailVerificationService")
    def test_email_verification_success(self, mock_email_verification_service):
        mock_service = mock_email_verification_service.return_value
        mock_service.verify_email.return_value = None

        data = {"email": "test@example.com", "token": "test_token"}
        response = self.client.post(self.verify_email_url, data, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["message"], "Email verificado com sucesso.")
        mock_service.verify_email.assert_called_once_with(email=Email("test@example.com"), token="test_token")

    @patch("accounts.views.EmailVerificationService")
    def test_email_verification_invalid_token(self, mock_email_verification_service):
        mock_service = mock_email_verification_service.return_value
        mock_service.verify_email.side_effect = InvalidVerificationTokenError("Token inválido ou expirado.")

        data = {"email": "test@example.com", "token": "invalid_token"}
        response = self.client.post(self.verify_email_url, data, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["detail"], "Token inválido ou expirado.")

    @patch('core.decorators.rate_limit', lambda *args, **kwargs: lambda func: func)
    @patch("accounts.views.EmailVerificationService")
    @patch("domain.accounts.services.email_verification_service.dispatcher.dispatch")
    def test_resend_verification_email_success(self, mock_dispatch, mock_email_verification_service):
        mock_service = mock_email_verification_service.return_value
        mock_user_entity = MagicMock(spec=UserEntity)
        mock_user_entity.email = Email("test@example.com")
        mock_user_entity.verification_token = "new_test_token"
        mock_user_entity.id = 1  # Adicionar um ID para o evento

        def side_effect_func(*args, **kwargs):
            mock_dispatch(
                UserRegistered(
                    user_id=mock_user_entity.id,
                    email=str(mock_user_entity.email),
                    verification_token=mock_user_entity.verification_token,
                )
            )
            return mock_user_entity

        mock_service.resend_verification_email.side_effect = side_effect_func

        data = {"email": "test@example.com"}
        response = self.client.post(self.resend_verification_url, data, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["message"], "Email de verificação reenviado com sucesso.")
        mock_service.resend_verification_email.assert_called_once_with(email=Email("test@example.com"))
        mock_dispatch.assert_called_once_with(
            UserRegistered(
                user_id=mock_user_entity.id,
                email=str(mock_user_entity.email),
                verification_token=mock_user_entity.verification_token,
            )
        )

    @patch("accounts.views.EmailVerificationService")
    def test_resend_verification_email_not_found(self, mock_email_verification_service):
        mock_service = mock_email_verification_service.return_value
        mock_service.resend_verification_email.side_effect = UserAlreadyExistsError("Usuário não encontrado.")

        data = {"email": "notfound@example.com"}
        response = self.client.post(self.resend_verification_url, data, format="json")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["detail"], "Usuário não encontrado.")

    @patch("accounts.views.ChangePasswordApplicationService")
    def test_change_password_success(self, mock_change_password_service):
        self.client.force_authenticate(user=self.user)
        mock_service = mock_change_password_service.return_value
        mock_service.change_password.return_value = None

        data = {
            "old_password": "oldpassword",
            "new_password": "newpassword123",
            "confirm_new_password": "newpassword123",
        }
        response = self.client.post(self.change_password_url, data, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["message"], "Senha alterada com sucesso.")
        mock_service.change_password.assert_called_once()

    @patch("accounts.views.ChangePasswordApplicationService")
    def test_change_password_invalid_old_password(self, mock_change_password_service):
        self.client.force_authenticate(user=self.user)
        mock_service = mock_change_password_service.return_value
        mock_service.change_password.side_effect = InvalidOldPasswordError("A senha antiga está incorreta.")

        data = {
            "old_password": "wrongpassword",
            "new_password": "newpassword123",
            "confirm_new_password": "newpassword123",
        }
        response = self.client.post(self.change_password_url, data, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["old_password"], "A senha antiga está incorreta.")

    def test_change_password_unauthenticated(self):
        data = {
            "old_password": "oldpassword",
            "new_password": "newpassword123",
            "confirm_new_password": "newpassword123",
        }
        response = self.client.post(self.change_password_url, data, format="json")
        self.assertEqual(response.status_code, 401)
