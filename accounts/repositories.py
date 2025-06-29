from django.contrib.auth import get_user_model
from domain.accounts.entities import User as UserEntity
from domain.accounts.repositories import AbstractUserRepository
from domain.accounts.value_objects.email import Email
DjangoUser = get_user_model()
class DjangoUserRepository(AbstractUserRepository):
    """Implementação do UserRepository usando o ORM do Django."""
    def add(self, user_entity: UserEntity) -> None:
        DjangoUser.objects.create(
            email=str(user_entity.email),
            first_name=user_entity.first_name,
            password=user_entity.hashed_password 
        )
    def exists_by_email(self, email: Email) -> bool:
        return DjangoUser.objects.filter(email=str(email)).exists()
