import abc

from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.interfaces import IPasswordHasher
from src.infrastructure.database.repository.abc import (
    ABCUsersRepository,
    AbstractRefreshTokenRepository,
    AbstractUserAuthStateRepository,
)
from src.infrastructure.database.repository.users import (
    SQLAlchemyUsersRepository,
    SqlAlchemyRefreshTokenRepository,
    SqlAlchemyUserAuthStateRepository,
)


class ABCUsersRepositoryFactory(abc.ABC):
    @abc.abstractmethod
    def create(self, session: AsyncSession) -> ABCUsersRepository:
        raise NotImplementedError


class SQLAlchemyUsersRepositoryFactory(ABCUsersRepositoryFactory):
    def __init__(self, hasher: IPasswordHasher):
        self._hasher = hasher

    def create(self, session: AsyncSession) -> SQLAlchemyUsersRepository:
        return SQLAlchemyUsersRepository(session)


class ABCRefreshTokenRepositoryFactory(abc.ABC):
    @abc.abstractmethod
    def create(self, session: AsyncSession) -> AbstractRefreshTokenRepository:
        raise NotImplementedError


class RefreshTokenRepositoryFactory(ABCRefreshTokenRepositoryFactory):
    def create(self, session: AsyncSession) -> SqlAlchemyRefreshTokenRepository:
        return SqlAlchemyRefreshTokenRepository(session)


class ABCUserAuthStateRepositoryFactory(abc.ABC):
    @abc.abstractmethod
    def create(self, session: AsyncSession) -> AbstractUserAuthStateRepository:
        raise NotImplementedError


class SqlAlchemyUserAuthStateRepositoryFactory(ABCUserAuthStateRepositoryFactory):
    def create(self, session: AsyncSession) -> AbstractUserAuthStateRepository:
        return SqlAlchemyUserAuthStateRepository(session)
