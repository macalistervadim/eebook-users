import abc

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src import config
from src.adapters import repository
from src.adapters.repository import AbstractRepository


class AbstractUnitOfWork(abc.ABC):
    users: AbstractRepository

    async def __aenter__(self) -> "AbstractUnitOfWork":
        return self

    async def __aexit__(self, *args) -> None:
        await self.rollback()

    async def commit(self) -> None:
        await self._commit()

    @abc.abstractmethod
    async def _commit(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def rollback(self) -> None:
        raise NotImplementedError


DEFAULT_SESSION_FACTORY = async_sessionmaker(
    bind=create_async_engine(
        config.get_postgres_uri(),
        isolation_level="REPEATABLE READ",
    ),
    expire_on_commit=False,
)


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session: AsyncSession = self.session_factory()
        self.users = repository.SqlAlchemyRepository(self.session)
        return await super().__aenter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        else:
            await self._commit()
        await self.session.close()
        return await super().__aexit__(exc_type, exc_val, exc_tb)

    async def _commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
