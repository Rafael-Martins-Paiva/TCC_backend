from dataclasses import dataclass, field
from .value_objects.email import Email
@dataclass
class User:
    """Entidade de domínio que representa um Usuário."""
    email: Email
    first_name: str
    hashed_password: str
    id: int | None = field(default=None, kw_only=True) 
