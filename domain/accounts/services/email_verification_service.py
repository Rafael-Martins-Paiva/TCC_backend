import secrets

from domain.events.dispatcher import dispatcher

from ..aggregates.account import User
from ..events.email_verified import EmailVerified
from ..events.user_registered import UserRegistered
from ..exceptions.auth_exceptions import InvalidVerificationTokenError, UserNotFoundError
from ..repositories.account_repository import AbstractUserRepository


class EmailVerificationService:
    def __init__(self, user_repository: AbstractUserRepository):
        self.user_repository = user_repository

    def verify_email(self, email: str, token: str) -> User:
        user = self.user_repository.get_by_email(email)
        if not user or user.verification_token != token:
            raise InvalidVerificationTokenError("Token de verificação inválido ou expirado.")

        user.is_verified = True
        user.verification_token = None
        self.user_repository.update(user)
        dispatcher.dispatch(EmailVerified(user_id=user.id, email=str(user.email)))
        return user

    def resend_verification_email(self, email: str) -> User:
        user = self.user_repository.get_by_email(email)
        if not user:
            raise UserNotFoundError(f"Usuário com e-mail {email} não encontrado.")

        if user.is_verified:
            return user

        new_token = secrets.token_urlsafe(32)
        user.verification_token = new_token
        self.user_repository.update(user)
        dispatcher.dispatch(
            UserRegistered(user_id=user.id, email=str(user.email), verification_token=user.verification_token)
        )
        return user
