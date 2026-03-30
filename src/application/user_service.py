import uuid

from src.adapters.abc_classes import ABCTimeProvider
from src.adapters.interfaces import IPasswordHasher
from src.application.auth_service import JWTAuthService
from src.application.uow import AbstractUnitOfWork
from src.domain.exceptions.exceptions import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    MaxLoginAttemptsExceeded,
    UserLockedError,
    UsernameAlreadyTakenError,
    UserNotFoundError,
)
from src.domain.model import User
from src.interfaces.api.schemas import TokenPair


class UserService:
    """Сервисный слой для работы с пользователями."""

    def __init__(
        self,
        uow: AbstractUnitOfWork,
        hasher: IPasswordHasher,
        time_provider: ABCTimeProvider,
        auth_service: JWTAuthService,
    ) -> None:
        self.uow = uow
        self.hasher = hasher
        self.time_provider = time_provider
        self.auth_service = auth_service

    async def register_user(
        self,
        first_name: str,
        last_name: str,
        email: str,
        username: str,
        password: str,
        fingerprint: str,
    ) -> tuple[User, TokenPair]:
        async with self.uow as uow:
            email = email.lower().strip()

            if await uow.users.get_by_email(email):
                raise EmailAlreadyRegisteredError(email)

            if username and await uow.users.get_by_username(username):
                raise UsernameAlreadyTakenError(username)

            now = self.time_provider.now()
            hashed = self.hasher.hash_password(password)

            user = User(
                user_id=None,
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                hashed_password=hashed,
                role=None,
                created_at=now,
                updated_at=now,
                last_login_at=None,
                is_verified=False,
            )

            await uow.users.add(user)
            await uow.commit()

            token_pair = await self.auth_service.create_token_pair(
                uow=uow,
                user_id=user.id,
                fingerprint=fingerprint,
            )

            return user, token_pair

    async def remove_user(self, user_id: uuid.UUID) -> None:
        async with self.uow as uow:
            await uow.users.remove(user_id)
            await uow.commit()

    async def login(
        self,
        email: str,
        password: str,
        fingerprint: str,
    ) -> TokenPair:
        async with self.uow as uow:
            try:
                token_pair = await self.auth_service.login(
                    uow=uow,
                    email=email,
                    password=password,
                    fingerprint=fingerprint,
                )
                await uow.commit()
                return token_pair
            except (
                InvalidCredentialsError,
                MaxLoginAttemptsExceeded,
                UserLockedError,
            ):
                await uow.commit()
                raise

    async def change_password(
        self,
        user_id: uuid.UUID,
        new_password: str,
    ) -> None:
        async with self.uow as uow:
            user = await uow.users.get_by_id(user_id)
            if not user:
                raise UserNotFoundError()

            hashed = self.hasher.hash_password(new_password)
            user.change_password(hashed, self.time_provider.now())

            await uow.users.update(user)
            await self.auth_service.invalidate_user_sessions(uow=uow, user_id=user_id)
            await uow.commit()

    async def verify_email(self, user_id: uuid.UUID) -> None:
        async with self.uow as uow:
            user = await uow.users.get_by_id(user_id)
            if not user:
                raise UserNotFoundError()

            user.verify_email(self.time_provider.now())
            await uow.users.update(user)
            await uow.commit()

    async def get_user_by_email(self, email: str) -> User | None:
        async with self.uow as uow:
            return await uow.users.get_by_email(email)

    async def get_user_by_id(self, user_id: uuid.UUID) -> User | None:
        async with self.uow as uow:
            return await uow.users.get_by_id(user_id)

    async def get_user_by_username(self, username: str) -> User | None:
        async with self.uow as uow:
            return await uow.users.get_by_username(username)
