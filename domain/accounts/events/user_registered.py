from dataclasses import dataclass

@dataclass(frozen=True)
class UserRegistered:
    user_id: int
    email: str
    verification_token: str
