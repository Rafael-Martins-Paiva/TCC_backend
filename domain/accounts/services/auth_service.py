import secrets
from ..factories.account_factory import UserFactory
from ..repositories.account_repository import AbstractUserRepository
from ..aggregates.account import User
from accounts.email_utils import send_verification_email

class UserAlreadyExistsError(Exception):
    pass

class RegistrationService:
    """Serviço de domínio para registrar um novo usuário."""
    def __init__(self, user_repository: AbstractUserRepository):
        self.user_repository = user_repository

    def register_user(self, email: str, first_name: str, last_name: str, password: str) -> User:
        verification_token = secrets.token_urlsafe(32)
        factory = UserFactory()
        user_entity = factory.create(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
            is_verified=False,
            verification_token=verification_token
        )
        if self.user_repository.exists_by_email(user_entity.email):
            raise UserAlreadyExistsError(f"Usuário com e-mail {email} já existe.")
        self.user_repository.add(user_entity)
        send_verification_email(str(user_entity.email), user_entity.verification_token)
        return user_entity


class InvalidVerificationTokenError(Exception):
    pass

class EmailVerificationService:
    """Serviço de domínio para verificar e-mails de usuários."""
    def __init__(self, user_repository: AbstractUserRepository):
        self.user_repository = user_repository

    def verify_email(self, email: str, token: str) -> User:
        user = self.user_repository.get_by_email(email)
        if not user or user.verification_token != token:
            raise InvalidVerificationTokenError("Token de verificação inválido ou expirado.")
        
        user.is_verified = True
        user.verification_token = None  # Limpa o token após a verificação
        self.user_repository.update(user)
        return user

    def resend_verification_email(self, email: str) -> User:
        user = self.user_repository.get_by_email(email)
        if not user:
            raise UserAlreadyExistsError(f"Usuário com e-mail {email} não encontrado.")
        
        if user.is_verified:
            # O usuário já está verificado, não precisa reenviar
            return user

        # Gera um novo token e atualiza o usuário
        new_token = secrets.token_urlsafe(32)
        user.verification_token = new_token
        self.user_repository.update(user)
        send_verification_email(str(user.email), user.verification_token)
        return user


class InvalidOldPasswordError(Exception):
    pass

class ChangePasswordService:
    """Serviço de domínio para mudar a senha do usuário."""
    def __init__(self, user_repository: AbstractUserRepository):
        self.user_repository = user_repository

    def change_password(self, user: User, old_password: str, new_password: str) -> User:
        if not user.check_password(old_password):
            raise InvalidOldPasswordError("Senha antiga inválida.")
        
        user.set_password(new_password)
        self.user_repository.update(user)
        return user

class UserProfileService:
    def __init__(self, user_repo: AbstractUserRepository):
        self.user_repo = user_repo

    def update_profile(self, user_id: int, update_data: dict):
        """
        Executa a lógica de negócio para atualizar um perfil.
        """
        user_entity = self.user_repo.get_by_id(user_id)

        # --- AQUI FICAM AS REGRAS DE NEGÓCIO ---
        # Exemplo 1: Validar o tamanho da bio
        if 'bio' in update_data and len(update_data['bio']) > 500:
            raise ValueError("A biografia não pode exceder 500 caracteres.")

        # Exemplo 2: Impedir a alteração de certos campos (segurança extra)
        if 'username' in update_data:
            raise ValueError("Não é permitido alterar o nome de usuário por esta rota.")

        # Atualiza a entidade com os dados validados
        for key, value in update_data.items():
            setattr(user_entity, key, value)

        # Persiste as alterações através do repositório
        self.user_repo.update(user_entity)