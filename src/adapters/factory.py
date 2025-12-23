import abc

from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.abc_repository import (
    ABCUsersRepository,
    ABCUsersSubscriptionRepository,
    AbstractRefreshTokenRepository,
    AbstractUserAuthStateRepository,
)
from src.adapters.interfaces import IPasswordHasher
from src.adapters.repository import (
    SqlAlchemyRefreshTokenRepository,
    SqlAlchemyUserAuthStateRepository,
    SQLAlchemyUsersRepository,
    SqlAlchemyUsersSubscriptionRepository,
)


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
        return SQLAlchemyUsersRepository(session)


class ABCRefreshTokenRepositoryFactory(abc.ABC):
    """Абстрактная фабрика для создания репозитория refresh токенов (JWT-auth)."""

    @abc.abstractmethod
    def create(self, session: AsyncSession) -> AbstractRefreshTokenRepository:
        """Создаёт экземпляр репозитория refresh токенов."""
        raise NotImplementedError


class RefreshTokenRepositoryFactory(ABCRefreshTokenRepositoryFactory):
    def create(self, session: AsyncSession) -> SqlAlchemyRefreshTokenRepository:
        return SqlAlchemyRefreshTokenRepository(session)


class ABCUsersSubscriptionRepositoryFactory(abc.ABC):
    """Абстрактная фабрика для создания репозитория подписок пользователей."""

    @abc.abstractmethod
    def create(self, session: AsyncSession) -> ABCUsersSubscriptionRepository:
        """Создаёт экземпляр репозитория подписок пользователей."""
        raise NotImplementedError


class SQLAlchemyUsersSubscriptionRepositoryFactory(ABCUsersSubscriptionRepositoryFactory):
    def create(self, session: AsyncSession) -> SqlAlchemyUsersSubscriptionRepository:
        return SqlAlchemyUsersSubscriptionRepository(session)


class ABCUserAuthStateRepositoryFactory(abc.ABC):
    @abc.abstractmethod
    def create(self, session: AsyncSession) -> AbstractUserAuthStateRepository:
        raise NotImplementedError


class SqlAlchemyUserAuthStateRepositoryFactory(ABCUserAuthStateRepositoryFactory):
    def create(self, session: AsyncSession) -> AbstractUserAuthStateRepository:
        return SqlAlchemyUserAuthStateRepository(session)
