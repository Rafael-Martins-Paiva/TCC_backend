from dataclasses import dataclass


@dataclass(frozen=True)
class EmailVerified:
    user_id: int
    email: str
