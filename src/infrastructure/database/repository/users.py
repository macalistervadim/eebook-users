import datetime
import uuid

from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.model import EmailVerificationToken, OutboxEvent, User, UserAuthState
from src.infrastructure.database.orm import (
    email_verification_tokens,
    outbox_events,
    refresh_tokens,
    user_auth_state,
    users,
)
from src.infrastructure.database.repository.abc import (
    ABCUsersRepository,
    AbstractEmailVerificationTokenRepository,
    AbstractOutboxEventRepository,
    AbstractRefreshTokenRepository,
    AbstractUserAuthStateRepository,
)
from src.schemas.internal.auth import RefreshToken


class SQLAlchemyUsersRepository(ABCUsersRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, user: User) -> None:
        stmt = users.insert().values(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            username=user.username,
            role=user.role,
            hashed_password=user.hashed_password,
            is_verified=user.is_verified,
            is_disabled=user.is_disabled,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login_at=user.last_login_at,
        )
        await self.session.execute(stmt)

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(users).where(users.c.email == email))
        row = result.first()
        return self._row_to_user(row) if row else None

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        result = await self.session.execute(select(users).where(users.c.id == user_id))
        row = result.first()
        return self._row_to_user(row) if row else None

    async def get_by_username(self, username: str) -> User | None:
        result = await self.session.execute(select(users).where(users.c.username == username))
        row = result.first()
        return self._row_to_user(row) if row else None

    async def update(self, user: User) -> None:
        stmt = (
            update(users)
            .where(users.c.id == user.id)
            .values(
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                username=user.username,
                hashed_password=user.hashed_password,
                is_verified=user.is_verified,
                is_disabled=user.is_disabled,
                updated_at=user.updated_at,
                role=user.role,
                last_login_at=user.last_login_at,
            )
        )
        await self.session.execute(stmt)

    async def remove(self, user_id: uuid.UUID) -> None:
        await self.session.execute(delete(users).where(users.c.id == user_id))

    def _row_to_user(self, row) -> User:
        record = row[0] if isinstance(row, tuple) else row
        return User(
            user_id=record.id,
            first_name=record.first_name,
            last_name=record.last_name,
            email=record.email,
            username=record.username,
            hashed_password=record.hashed_password,
            role=record.role,
            is_verified=record.is_verified,
            is_disabled=record.is_disabled,
            created_at=record.created_at,
            updated_at=record.updated_at,
            last_login_at=record.last_login_at,
        )


class SqlAlchemyRefreshTokenRepository(AbstractRefreshTokenRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, token: RefreshToken) -> None:
        await self.session.execute(
            insert(refresh_tokens).values(
                id=token.id,
                user_id=token.user_id,
                jti=str(token.jti),
                fingerprint=token.fingerprint,
                created_at=token.created_at,
                expires_at=token.expires_at,
                is_revoked=token.is_revoked,
            ),
        )

    async def get_by_id(self, token_id: uuid.UUID) -> RefreshToken | None:
        return await self.session.get(RefreshToken, token_id)

    async def revoke(self, token_id: uuid.UUID, now: datetime.datetime) -> None:
        await self.session.execute(
            update(refresh_tokens).where(refresh_tokens.c.id == token_id).values(is_revoked=True),
        )

    async def revoke_all_for_user(self, user_id: uuid.UUID, now: datetime.datetime) -> None:
        await self.session.execute(
            update(refresh_tokens).where(refresh_tokens.c.user_id == user_id).values(is_revoked=True),
        )

    async def update(self, token: RefreshToken) -> None:
        await self.session.execute(
            update(refresh_tokens)
            .where(refresh_tokens.c.id == token.id)
            .values(
                id=token.id,
                user_id=token.user_id,
                jti=token.jti,
                fingerprint=token.fingerprint,
                created_at=token.created_at,
                expires_at=token.expires_at,
                is_revoked=token.is_revoked,
            ),
        )


class SqlAlchemyUserAuthStateRepository(AbstractUserAuthStateRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_user_id(self, user_id: uuid.UUID) -> UserAuthState | None:
        result = await self.session.execute(
            select(user_auth_state).where(user_auth_state.c.user_id == user_id),
        )
        row = result.first()
        if not row:
            return None

        data = row._mapping
        return UserAuthState(
            user_id=data['user_id'],
            failed_attempts=data['failed_attempts'],
            token_version=data['token_version'],
            locked_until=data['locked_until'],
            last_failed_at=data['last_failed_at'],
            lock_count=data['lock_count'],
        )

    async def create(self, state: UserAuthState) -> None:
        await self.session.execute(
            insert(user_auth_state).values(
                user_id=state.user_id,
                failed_attempts=state.failed_attempts,
                token_version=state.token_version,
                locked_until=state.locked_until,
                last_failed_at=state.last_failed_at,
                lock_count=state.lock_count,
            ),
        )

    async def save(self, state: UserAuthState) -> None:
        await self.session.execute(
            update(user_auth_state)
            .where(user_auth_state.c.user_id == state.user_id)
            .values(
                failed_attempts=state.failed_attempts,
                token_version=state.token_version,
                locked_until=state.locked_until,
                last_failed_at=state.last_failed_at,
                lock_count=state.lock_count,
            ),
        )


class SqlAlchemyEmailVerificationTokenRepository(AbstractEmailVerificationTokenRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, token: EmailVerificationToken) -> None:
        await self.session.execute(
            insert(email_verification_tokens).values(
                id=token.id,
                user_id=token.user_id,
                token_hash=token.token_hash,
                expires_at=token.expires_at,
                created_at=token.created_at,
                used_at=token.used_at,
            ),
        )

    async def get_active_by_token_hash(self, token_hash: str) -> EmailVerificationToken | None:
        result = await self.session.execute(
            select(email_verification_tokens).where(email_verification_tokens.c.token_hash == token_hash),
        )
        row = result.first()
        if not row:
            return None

        data = row._mapping
        return EmailVerificationToken(
            id=data['id'],
            user_id=data['user_id'],
            token_hash=data['token_hash'],
            expires_at=data['expires_at'],
            created_at=data['created_at'],
            used_at=data['used_at'],
        )

    async def revoke_active_for_user(self, user_id: uuid.UUID, now: datetime.datetime) -> None:
        await self.session.execute(
            update(email_verification_tokens)
            .where(
                email_verification_tokens.c.user_id == user_id,
                email_verification_tokens.c.used_at.is_(None),
            )
            .values(used_at=now),
        )

    async def save(self, token: EmailVerificationToken) -> None:
        await self.session.execute(
            update(email_verification_tokens)
            .where(email_verification_tokens.c.id == token.id)
            .values(
                user_id=token.user_id,
                token_hash=token.token_hash,
                expires_at=token.expires_at,
                created_at=token.created_at,
                used_at=token.used_at,
            ),
        )


class SqlAlchemyOutboxEventRepository(AbstractOutboxEventRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, event: OutboxEvent) -> None:
        await self.session.execute(
            insert(outbox_events).values(
                id=event.id,
                event_type=event.event_type,
                routing_key=event.routing_key,
                payload=event.payload,
                created_at=event.created_at,
                published_at=event.published_at,
                error_message=event.error_message,
                attempts=event.attempts,
            ),
        )

    async def list_pending(self, limit: int) -> list[OutboxEvent]:
        result = await self.session.execute(
            select(outbox_events)
            .where(outbox_events.c.published_at.is_(None))
            .order_by(outbox_events.c.created_at.asc())
            .limit(limit),
        )
        rows = result.fetchall()
        return [
            OutboxEvent(
                id=row._mapping['id'],
                event_type=row._mapping['event_type'],
                routing_key=row._mapping['routing_key'],
                payload=row._mapping['payload'],
                created_at=row._mapping['created_at'],
                published_at=row._mapping['published_at'],
                error_message=row._mapping['error_message'],
                attempts=row._mapping['attempts'],
            )
            for row in rows
        ]

    async def save(self, event: OutboxEvent) -> None:
        await self.session.execute(
            update(outbox_events)
            .where(outbox_events.c.id == event.id)
            .values(
                published_at=event.published_at,
                error_message=event.error_message,
                attempts=event.attempts,
            ),
        )
