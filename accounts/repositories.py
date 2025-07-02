from django.contrib.auth import get_user_model
from domain.accounts.aggregates.account import User as UserEntity
from domain.accounts.repositories.account_repository import AbstractUserRepository
from domain.accounts.aggregates.value_objects.email import Email

DjangoUser = get_user_model()

class DjangoUserRepository(AbstractUserRepository):
    """Implementação do UserRepository usando o ORM do Django."""

    def add(self, user_entity: UserEntity) -> None:
        DjangoUser.objects.create(
            email=str(user_entity.email),
            first_name=user_entity.first_name,
            last_name=user_entity.last_name,
            password=user_entity.hashed_password,
            is_verified=user_entity.is_verified,
            verification_token=user_entity.verification_token
        )

    def exists_by_email(self, email: Email) -> bool:
        return DjangoUser.objects.filter(email=str(email)).exists()

    def get_by_email(self, email: Email) -> UserEntity | None:
        try:
            django_user = DjangoUser.objects.get(email=str(email))
            return UserEntity(
                id=django_user.id,
                email=Email(django_user.email),
                first_name=django_user.first_name,
                last_name=django_user.last_name,
                hashed_password=django_user.password,
                is_verified=django_user.is_verified,
                verification_token=django_user.verification_token
            )
        except DjangoUser.DoesNotExist:
            return None

    def update(self, user_entity: UserEntity) -> None:
        django_user = DjangoUser.objects.get(id=user_entity.id)
        django_user.email = str(user_entity.email)
        django_user.first_name = user_entity.first_name
        django_user.last_name = user_entity.last_name
        django_user.password = user_entity.hashed_password
        django_user.is_verified = user_entity.is_verified
        django_user.verification_token = user_entity.verification_token
        django_user.bio = user_entity.bio
        django_user.save()

    def get_by_id(self, user_id: int) -> UserEntity:
        user_model = DjangoUser.objects.get(id=user_id)
        # Converte o modelo do Django para uma entidade de domínio
        return self._to_entity(user_model)

    def _to_entity(self, user_model: DjangoUser) -> UserEntity:
        # Lógica para converter o modelo do ORM para a entidade de domínio
        return UserEntity(
            id=user_model.id,
            email=Email(user_model.email),
            first_name=user_model.first_name,
            last_name=user_model.last_name,
            hashed_password=user_model.password,
            is_verified=user_model.is_verified,
            verification_token=user_model.verification_token,
            bio=getattr(user_model, 'bio', '')
        )
