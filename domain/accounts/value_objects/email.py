from dataclasses import dataclass
from email_validator import validate_email, EmailNotValidError
class InvalidEmailError(ValueError):
    """Exceção customizada para e-mails inválidos."""
    pass
@dataclass(frozen=True)
class Email:
    """
    Um Value Object que representa um endereço de e-mail.
    
    É imutável (frozen=True) e auto-validado na sua criação.
    Usa uma biblioteca robusta em vez de regex simples.
    """
    value: str
    def __post_init__(self):
        try:
            
            
            
            valid = validate_email(self.value, check_deliverability=False)
            
            
            
            object.__setattr__(self, 'value', valid.normalized)
        except EmailNotValidError as e:
            
            raise InvalidEmailError(f"Endereço de e-mail inválido: {self.value}") from e
    def __str__(self) -> str:
        return self.value
