from dataclasses import dataclass

from email_validator import EmailNotValidError, validate_email


class InvalidEmailError(ValueError):
    pass


@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self):
        try:

            valid = validate_email(self.value, check_deliverability=False)

            object.__setattr__(self, "value", valid.normalized)
        except EmailNotValidError as e:

            raise InvalidEmailError(f"Endereço de e-mail inválido: {self.value}") from e

    def __str__(self) -> str:
        return self.value
