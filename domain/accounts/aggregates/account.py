from dataclasses import dataclass, field
from django.contrib.auth.hashers import make_password, check_password
from .value_objects.email import Email

@dataclass
class User:
    email: Email
    name: str
    hashed_password: str
    is_verified: bool = False
    verification_token: str | None = None
    bio: str = ""
    id: int | None = field(default=None, kw_only=True)

    def set_password(self, raw_password: str):
        self.hashed_password = make_password(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password(raw_password, self.hashed_password)

    def set_bio(self, bio: str):
        if len(bio) > 500:
            raise ValueError("A biografia não pode exceder 500 caracteres.")
        self.bio = bio 
