import abc
from .entities import User
from .value_objects.email import Email
class AbstractUserRepository(abc.ABC):
    """
    Define a interface (contrato) para um repositório de usuários.
    Isso permite a inversão de dependência.
    """
    @abc.abstractmethod
    def add(self, user: User) -> None:
        raise NotImplementedError
    @abc.abstractmethod
    def exists_by_email(self, email: Email) -> bool:
        raise NotImplementedError
