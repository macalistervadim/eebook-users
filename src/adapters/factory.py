import abc

from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.interfaces import IPasswordHasher
from src.adapters.repository import ABCUsersRepository, SQLAlchemyUsersRepository


class ABCUsersRepositoryFactory(abc.ABC):
    """Абстрактная фабрика для создания репозитория пользователей."""

    @abc.abstractmethod
    def create(self, session: AsyncSession) -> ABCUsersRepository:
        """Создаёт экземпляр репозитория пользователей."""
        raise NotImplementedError


class SQLAlchemyUsersRepositoryFactory(ABCUsersRepositoryFactory):
    def __init__(self, hasher: IPasswordHasher):
        self._hasher = hasher

    def create(self, session: AsyncSession) -> SQLAlchemyUsersRepository:
        return SQLAlchemyUsersRepository(session, self._hasher)
