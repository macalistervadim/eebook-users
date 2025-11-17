import logging
from functools import lru_cache

from src.adapters.factory import ABCUsersRepositoryFactory, SQLAlchemyUsersRepositoryFactory
from src.adapters.interfaces import IPasswordHasher
from src.adapters.password_hasher import Argon2PasswordHasher
from src.config.settings import Settings
from src.infrastructure.database.engine import get_session_factory
from src.service_layer.uow import AbstractUnitOfWork, SqlAlchemyUnitOfWork
from src.service_layer.users_service import UserService

logger = logging.getLogger(__name__)


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore


async def get_uow() -> AbstractUnitOfWork:
    return SqlAlchemyUnitOfWork(
        session_factory=get_session_factory(),
        repo_factory=await get_repo_factory(),
    )


async def get_repo_factory() -> ABCUsersRepositoryFactory:
    return SQLAlchemyUsersRepositoryFactory(await get_hasher())


async def get_hasher() -> IPasswordHasher:
    return Argon2PasswordHasher()


async def get_user_service() -> UserService:
    uow = await get_uow()
    hasher = await get_hasher()
    return UserService(uow=uow, hasher=hasher)
