from dataclasses import dataclass

@dataclass(frozen=True)
class PasswordChanged:
    user_id: int
    email: str
