from ..aggregates.account import User
from ..exceptions.auth_exceptions import InvalidCredentialsError, UserNotFoundError, UserNotVerifiedError
from ..repositories.account_repository import AbstractUserRepository


class AuthService:
    def __init__(self, user_repository: AbstractUserRepository):
        self.user_repository = user_repository

    def login(self, email: str, password: str) -> User:
        user = self.user_repository.get_by_email(email)
        if not user:
            raise UserNotFoundError(f"Usuário com e-mail {email} não encontrado.")

        if not user.check_password(password):
            raise InvalidCredentialsError("Credenciais inválidas.")

        if not user.is_verified:
            raise UserNotVerifiedError("Usuário não verificado.")

        return user
