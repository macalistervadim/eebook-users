import logging
from datetime import timedelta
from typing import AsyncIterator

from httpx import AsyncClient

from src.adapters.abc_classes import ABCTimeProvider
from src.adapters.auth.jwt_backend import JwtTokenAdapter
from src.adapters.interfaces import IPasswordHasher
from src.adapters.password_hasher import Argon2PasswordHasher
from src.adapters.time_provider import UtcTimeProvider
from src.application.auth_service import JWTAuthService
from src.application.uow import AbstractUnitOfWork, SqlAlchemyUnitOfWork
from src.application.user_service import UserService
from src.config.settings import get_settings
from src.infrastructure.clients.subscriptions import SubscriptionsClient
from src.infrastructure.database.engine import get_session_factory
from src.infrastructure.database.repository.factory import (
    ABCRefreshTokenRepositoryFactory,
    ABCUserAuthStateRepositoryFactory,
    ABCUsersRepositoryFactory,
    RefreshTokenRepositoryFactory,
    SqlAlchemyUserAuthStateRepositoryFactory,
    SQLAlchemyUsersRepositoryFactory,
)

logger = logging.getLogger(__name__)


async def get_uow() -> AbstractUnitOfWork:
    return SqlAlchemyUnitOfWork(
        session_factory=get_session_factory(),
        repo_factory=await get_repo_factory(),
        refresh_token_repo_factory=await get_refresh_token_repo_factory(),
        user_auth_state_repo_factory=await get_user_auth_state_repo_factory(),
    )


async def get_user_auth_state_repo_factory() -> ABCUserAuthStateRepositoryFactory:
    return SqlAlchemyUserAuthStateRepositoryFactory()


async def get_repo_factory() -> ABCUsersRepositoryFactory:
    return SQLAlchemyUsersRepositoryFactory(await get_hasher())


async def get_hasher() -> IPasswordHasher:
    return Argon2PasswordHasher()


async def get_time_provider() -> ABCTimeProvider:
    return UtcTimeProvider()


async def get_jwt_backend() -> JwtTokenAdapter:
    settings = get_settings()
    algorithm = settings.JWT_ALGORITHM

    if algorithm == 'HS256':
        signing_key = settings.JWT_SECRET or settings.FASTAPI_SECRET
        verification_key = signing_key
    else:
        signing_key = (settings.JWT_PRIVATE_KEY or '').replace('\\n', '\n')
        verification_key = (settings.JWT_PUBLIC_KEY or '').replace('\\n', '\n')

    if not signing_key or not verification_key:
        raise RuntimeError('JWT signing/verification keys are not configured')

    return JwtTokenAdapter(
        signing_key=signing_key,
        verification_key=verification_key,
        algorithm=algorithm,
        access_expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_TTL_MINUTES),
        refresh_expires_delta=timedelta(days=settings.REFRESH_TOKEN_TTL_DAYS),
        time_provider=await get_time_provider(),
    )


async def get_refresh_token_repo_factory() -> ABCRefreshTokenRepositoryFactory:
    return RefreshTokenRepositoryFactory()


async def get_subscriptions_client() -> AsyncIterator[SubscriptionsClient]:
    settings = get_settings()
    base_url = settings.SUBSCRIPTIONS_SERVICE_URL
    if not base_url:
        yield SubscriptionsClient(http_client=None)
        return

    async with AsyncClient(
        base_url=base_url.rstrip('/'),
        timeout=5.0,
    ) as http_client:
        yield SubscriptionsClient(http_client=http_client)


async def get_auth_service() -> JWTAuthService:
    settings = get_settings()
    return JWTAuthService(
        jwt_backend=await get_jwt_backend(),
        time_provider=await get_time_provider(),
        hasher=await get_hasher(),
        max_attempts=settings.MAX_LOGIN_ATTEMPTS,
        lock_time=timedelta(minutes=settings.LOGIN_LOCK_MINUTES),
    )


async def get_user_service() -> UserService:
    return UserService(
        uow=await get_uow(),
        hasher=await get_hasher(),
        time_provider=await get_time_provider(),
        auth_service=await get_auth_service(),
    )
