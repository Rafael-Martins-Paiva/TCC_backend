from .factories import UserFactory
from .repositories import AbstractUserRepository
from .entities import User
class UserAlreadyExistsError(Exception):
    pass
class RegistrationService:
    """Serviço de domínio para registrar um novo usuário."""
    def __init__(self, user_repository: AbstractUserRepository):
        self.user_repository = user_repository
    def register_user(self, email: str, first_name: str, password: str) -> User:
        factory = UserFactory()
        user_entity = factory.create(email=email, first_name=first_name, password=password)
        if self.user_repository.exists_by_email(user_entity.email):
            raise UserAlreadyExistsError(f"Usuário com e-mail {email} já existe.")
        self.user_repository.add(user_entity)
        return user_entity
