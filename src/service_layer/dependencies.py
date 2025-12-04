import logging
from datetime import timedelta

from redis.asyncio import Redis

from src.adapters.abc_classes import ABCAuthService, ABCTimeProvider, ABCTokenStore
from src.adapters.auth.jwt_backend import JwtTokenAdapter
from src.adapters.factory import (
    ABCRefreshTokenRepositoryFactory,
    ABCUsersRepositoryFactory,
    RefreshTokenRepositoryFactory,
    SQLAlchemyUsersRepositoryFactory,
)
from src.adapters.interfaces import IPasswordHasher
from src.adapters.password_hasher import Argon2PasswordHasher
from src.adapters.time_provider import UtcTimeProvider
from src.infrastructure.auth.token_store import RedisJwtRevocationStore
from src.infrastructure.database.engine import get_session_factory
from src.service_layer.auth_service import JWTAuthService
from src.service_layer.uow import AbstractUnitOfWork, SqlAlchemyUnitOfWork
from src.service_layer.users_service import UserService

logger = logging.getLogger(__name__)


async def get_uow() -> AbstractUnitOfWork:
    session_factory = get_session_factory()

    return SqlAlchemyUnitOfWork(
        session_factory=session_factory,
        repo_factory=await get_repo_factory(),
        refresh_token_repo_factory=await get_refresh_token_repo_factory(),
    )


async def get_repo_factory() -> ABCUsersRepositoryFactory:
    return SQLAlchemyUsersRepositoryFactory(await get_hasher())


async def get_hasher() -> IPasswordHasher:
    return Argon2PasswordHasher()


async def get_time_provider() -> ABCTimeProvider:
    return UtcTimeProvider()


async def get_jwt_backend():
    return JwtTokenAdapter(
        secret_key='123',
        access_expires_delta=timedelta(minutes=15),
        refresh_expires_delta=timedelta(days=7),
        time_provider=await get_time_provider(),
    )


async def get_token_store() -> ABCTokenStore:
    return RedisJwtRevocationStore(
        redis=Redis.from_url(
            'redis://:eYVX7EwVmmxKPCDmwMtyKVge8oLd2t81@redis:6379/0',
            decode_responses=False,
            health_check_interval=30,
        ),
    )


async def get_refresh_token_repo_factory() -> ABCRefreshTokenRepositoryFactory:
    return RefreshTokenRepositoryFactory()


async def get_auth_service() -> ABCAuthService:
    return JWTAuthService(
        jwt_backend=await get_jwt_backend(),
        token_store=await get_token_store(),
        time_provider=await get_time_provider(),
    )


async def get_user_service() -> UserService:
    uow = await get_uow()
    hasher = await get_hasher()
    time_provider = await get_time_provider()
    auth_service = await get_auth_service()
    return UserService(
        uow=uow,
        hasher=hasher,
        time_provider=time_provider,
        auth_service=auth_service,
    )
