import secrets

from domain.events.dispatcher import dispatcher

from ..aggregates.account import User
from ..events.user_registered import UserRegistered
from ..exceptions.auth_exceptions import UserAlreadyExistsError
from ..factories.account_factory import UserFactory
from ..repositories.account_repository import AbstractUserRepository


class RegistrationService:
    def __init__(self, user_repository: AbstractUserRepository):
        self.user_repository = user_repository

    def register_user(self, email: str, name: str, password: str) -> User:
        verification_token = secrets.token_urlsafe(32)
        user_entity = UserFactory.create(
            email=email, name=name, password=password, is_verified=False, verification_token=verification_token
        )
        if self.user_repository.exists_by_email(user_entity.email):
            raise UserAlreadyExistsError(f"Usuário com e-mail {email} já existe.")
        self.user_repository.add(user_entity)
        dispatcher.dispatch(
            UserRegistered(
                user_id=user_entity.id, email=str(user_entity.email), verification_token=user_entity.verification_token
            )
        )
        return user_entity
