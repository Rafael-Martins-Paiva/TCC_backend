from django.contrib.auth import get_user_model
from domain.accounts.services.change_password_service import ChangePasswordService
from domain.accounts.exceptions.auth_exceptions import InvalidOldPasswordError
from domain.accounts.services.user_profile_service import UserProfileService
from accounts.repositories import DjangoUserRepository

User = get_user_model()

class ChangePasswordApplicationService:
    def __init__(self):
        self.user_repository = DjangoUserRepository()
        self.change_password_domain_service = ChangePasswordService(self.user_repository)

    def change_password(self, user: User, old_password: str, new_password: str) -> User:
        try:
            user_entity = self.user_repository._to_entity(user)
            updated_user_entity = self.change_password_domain_service.change_password(user_entity, old_password, new_password)
            return User.objects.get(id=updated_user_entity.id)
        except InvalidOldPasswordError as e:
            raise e

class UserApplicationService:
    def __init__(self):
        user_repository = DjangoUserRepository()
        self.domain_service = UserProfileService(user_repository)

    def update_user_info(self, user_id: int, data: dict) -> User:
        self.domain_service.update_profile(user_id=user_id, update_data=data)

        return User.objects.get(id=user_id)
