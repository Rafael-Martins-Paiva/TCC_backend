from django.contrib.auth.hashers import make_password
from ..aggregates.account import User
from ..aggregates.value_objects.email import Email
class UserFactory:
    """Fábrica para criar instâncias da entidade User."""
    @staticmethod
    def create(email: str, first_name: str, last_name: str, password: str, is_verified: bool = False, verification_token: str | None = None) -> User:
        """
        Cria uma entidade User a partir de dados primitivos.
        Encapsula a criação do Value Object Email e o hashing da senha.
        """
        email_vo = Email(email) 
        
        
        
        hashed_password = make_password(password)
        return User(
            email=email_vo,
            first_name=first_name,
            last_name=last_name,
            hashed_password=hashed_password,
            is_verified=is_verified,
            verification_token=verification_token
        )
