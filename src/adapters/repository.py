import abc

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.model import User


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, user: User) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def add(self, user: User) -> None:
        """
        Add a new user to the repository.

        :param user: User
        :return:
        """
        self.session.add(user)

    async def get_by_email(self, email: str) -> User | None:
        """
        Get a user by email.

        :param email: user email
        :return: User | None
        """
        result = await self.session.execute(
            select(User).where(User.email == email),
        )
        return result.scalars().first()
