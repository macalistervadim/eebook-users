import abc

from sqlalchemy.orm import Session

from src.domain.model import User


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, user: User) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, user_id: str) -> User | None:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session: Session):
        self.session = session

    def add(self, user: User) -> None:
        """
        Add a new user to the repository.

        :param user: User
        :return:
        """
        self.session.add(user)

    def get(self, user_id: str) -> User | None:
        """
        Get a user by id.

        :param user_id: str
        :return:
        """
        user_id = str(user_id)  # Ensure user_id is a string
        return self.session.query(User).filter(User.id == user_id).first()
