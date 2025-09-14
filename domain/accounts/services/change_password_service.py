from domain.events.dispatcher import dispatcher

from ..aggregates.account import User
from ..events.password_changed import PasswordChanged
from ..exceptions.auth_exceptions import InvalidOldPasswordError
from ..repositories.account_repository import AbstractUserRepository


class ChangePasswordService:
    def __init__(self, user_repository: AbstractUserRepository):
        self.user_repository = user_repository

    def change_password(self, user: User, old_password: str, new_password: str) -> User:
        if not user.check_password(old_password):
            raise InvalidOldPasswordError("Senha antiga inválida.")

        user.set_password(new_password)
        self.user_repository.update(user)
        dispatcher.dispatch(PasswordChanged(user_id=user.id, email=str(user.email)))
        return user
