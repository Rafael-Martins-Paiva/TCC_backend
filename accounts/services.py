from django.contrib.auth import get_user_model
from domain.accounts.services.auth_service import ChangePasswordService, InvalidOldPasswordError, UserProfileService
from accounts.repositories import DjangoUserRepository

User = get_user_model()

class UserService:
    def create_user(self, user_data: dict) -> User:
        """
        Cria um novo usuário no sistema usando o CustomUserManager.
        """
        
        password = user_data.pop('password')
        email = user_data.pop('email')
        
        
        
        user_data.pop('password2', None)
        
        
        user = User.objects.create_user(email=email, password=password, **user_data)
        
        return user


class ChangePasswordApplicationService:
    """Serviço de aplicação para mudança de senha."""
    def __init__(self):
        self.user_repository = DjangoUserRepository()
        self.change_password_domain_service = ChangePasswordService(self.user_repository)

    def change_password(self, user: User, old_password: str, new_password: str) -> User:
        try:
            updated_user = self.change_password_domain_service.change_password(user, old_password, new_password)
            return updated_user
        except InvalidOldPasswordError as e:
            raise e

class UserApplicationService:
    def __init__(self):
        # A implementação concreta do repositório é injetada aqui
        user_repository = DjangoUserRepository()
        # O serviço de domínio recebe a abstração do repositório
        self.domain_service = UserProfileService(user_repository)

    def update_user_info(self, user_id: int, data: dict) -> User:
        """
        Orquestra a atualização de informações do usuário.
        """
        # Chama a lógica de negócio real no serviço de domínio
        self.domain_service.update_profile(user_id=user_id, update_data=data)

        # Retorna o modelo Django atualizado para a View
        return User.objects.get(id=user_id)