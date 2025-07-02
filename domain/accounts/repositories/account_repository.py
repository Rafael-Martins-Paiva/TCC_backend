import abc
from ..aggregates.account import User
from ..aggregates.value_objects.email import Email
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

    @abc.abstractmethod
    def get_by_id(self, user_id: int) -> User:
        raise NotImplementedError

    @abc.abstractmethod
    def update(self, user: User):
        raise NotImplementedError
