import json
import uuid
from datetime import timedelta

from src.adapters.abc_classes import ABCTimeProvider
from src.adapters.interfaces import IPasswordHasher
from src.application.auth_service import JWTAuthService
from src.application.uow import AbstractUnitOfWork
from src.application.utils import generate_email_verification_token, hash_email_verification_token
from src.domain.exceptions.exceptions import (
    EmailAlreadyRegisteredError,
    EmailAlreadyVerifiedError,
    InvalidCredentialsError,
    InvalidEmailVerificationTokenError,
    MaxLoginAttemptsExceeded,
    UserLockedError,
    UserNotFoundError,
    UsernameAlreadyTakenError,
)
from src.domain.model import EmailVerificationToken, OutboxEvent, User
from src.interfaces.api.schemas import RegistrationPendingSchema, TokenPair


class UserService:
    """Сервисный слой для работы с пользователями."""

    def __init__(
        self,
        uow: AbstractUnitOfWork,
        hasher: IPasswordHasher,
        time_provider: ABCTimeProvider,
        auth_service: JWTAuthService,
        email_verification_ttl: timedelta,
        frontend_base_url: str,
        rabbitmq_exchange: str,
    ) -> None:
        self.uow = uow
        self.hasher = hasher
        self.time_provider = time_provider
        self.auth_service = auth_service
        self.email_verification_ttl = email_verification_ttl
        self.frontend_base_url = frontend_base_url.rstrip('/')
        self.rabbitmq_exchange = rabbitmq_exchange

    async def register_user(
        self,
        first_name: str,
        last_name: str,
        email: str,
        username: str,
        password: str,
    ) -> RegistrationPendingSchema:
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
            raw_token = await self._issue_email_verification(uow=uow, user=user, now=now)
            await uow.commit()

            return RegistrationPendingSchema(
                user_id=str(user.id),
                email=user.email,
                requires_email_verification=True,
                message='Verification email has been scheduled',
                debug_verification_token=raw_token,
            )

    async def _issue_email_verification(
        self,
        *,
        uow: AbstractUnitOfWork,
        user: User,
        now,
    ) -> str:
        await uow.email_verification_tokens.revoke_active_for_user(user.id, now)

        raw_token = generate_email_verification_token()
        token = EmailVerificationToken(
            id=uuid.uuid4(),
            user_id=user.id,
            token_hash=hash_email_verification_token(raw_token),
            created_at=now,
            expires_at=now + self.email_verification_ttl,
        )
        await uow.email_verification_tokens.add(token)

        verification_url = f'{self.frontend_base_url}/verify-email?token={raw_token}'
        event = OutboxEvent(
            id=uuid.uuid4(),
            event_type='user.email_verification_requested',
            routing_key='notifications.email.verification.requested',
            payload=json.dumps(
                {
                    'event_id': str(uuid.uuid4()),
                    'event_type': 'user.email_verification_requested',
                    'exchange': self.rabbitmq_exchange,
                    'occurred_at': now.isoformat(),
                    'payload': {
                        'user_id': str(user.id),
                        'email': user.email,
                        'first_name': user.first_name,
                        'verification_url': verification_url,
                        'expires_at': token.expires_at.isoformat(),
                    },
                },
            ),
            created_at=now,
        )
        await uow.outbox_events.add(event)
        return raw_token

    async def resend_verification_email(self, email: str) -> None:
        async with self.uow as uow:
            normalized_email = email.lower().strip()
            user = await uow.users.get_by_email(normalized_email)
            if user is None or user.is_verified:
                return

            now = self.time_provider.now()
            await self._issue_email_verification(uow=uow, user=user, now=now)
            await uow.commit()

    async def verify_email_token(self, token: str) -> None:
        token_hash = hash_email_verification_token(token.strip())
        if not token_hash:
            raise InvalidEmailVerificationTokenError()

        async with self.uow as uow:
            verification = await uow.email_verification_tokens.get_active_by_token_hash(token_hash)
            if verification is None:
                raise InvalidEmailVerificationTokenError()

            now = self.time_provider.now()
            verification.ensure_active(now)
            user = await uow.users.get_by_id(verification.user_id)
            if user is None:
                raise UserNotFoundError()
            if user.is_verified:
                raise EmailAlreadyVerifiedError()

            verification.mark_used(now)
            user.verify_email(now)
            await uow.email_verification_tokens.save(verification)
            await uow.users.update(user)
            await uow.commit()

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
