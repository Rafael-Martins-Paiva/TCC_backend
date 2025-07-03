from ..aggregates.account import User
from ..aggregates.value_objects.email import Email

class UserFactory:
    @staticmethod
    def create(email: str, name: str, password: str, is_verified: bool = False, verification_token: str | None = None) -> User:
        email_vo = Email(email)
        user = User(
            email=email_vo,
            name=name,
            is_verified=is_verified,
            verification_token=verification_token,
            hashed_password="" # Temporário, será definido por set_password
        )
        user.set_password(password)
        return user
