import datetime
import uuid

from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.abc_repository import (
    ABCUsersRepository,
    ABCUsersSubscriptionRepository,
    AbstractRefreshTokenRepository,
    AbstractUserAuthStateRepository,
)
from src.adapters.orm import refresh_tokens, user_auth_state, users
from src.adapters.orm import user_subscription as user_sub_table
from src.domain.model import User, UserAuthState, UserSubscription
from src.schemas.internal.auth import RefreshToken


class SQLAlchemyUsersRepository(ABCUsersRepository):
    """Реализация репозитория пользователей на SQLAlchemy (PostgreSQL, async) с поддержкой UoW."""

    def __init__(self, session: AsyncSession):
        """Инициализирует репозиторий пользователей.

        Args:
            session: Асинхронная сессия SQLAlchemy.
            hasher: Сервис для хеширования паролей.

        """
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
                updated_at=user.updated_at,
                role=user.role,
                last_login_at=user.last_login_at,
            )
        )
        await self.session.execute(stmt)

    async def remove(self, user_id: uuid.UUID) -> None:
        stmt = delete(users).where(users.c.id == user_id)
        await self.session.execute(stmt)

    def _row_to_user(self, row) -> User:
        """Конвертирует строку результата SQLAlchemy в доменную модель User.

        Args:
            row: Строка результата запроса SQLAlchemy.

        Returns:
            Экземпляр доменной модели User.

        Note:
            Внутренний метод, не предназначен для использования извне.

        """
        r = row[0] if isinstance(row, tuple) else row
        return User(
            user_id=r.id,
            first_name=r.first_name,
            last_name=r.last_name,
            email=r.email,
            username=r.username,
            hashed_password=r.hashed_password,
            role=r.role,
            is_verified=r.is_verified,
            created_at=r.created_at,
            updated_at=r.updated_at,
            last_login_at=r.last_login_at,
        )


class SqlAlchemyRefreshTokenRepository(AbstractRefreshTokenRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, token: RefreshToken) -> None:
        stmt = insert(refresh_tokens).values(
            id=token.id,
            user_id=token.user_id,
            jti=str(token.jti),
            fingerprint=token.fingerprint,
            created_at=token.created_at,
            expires_at=token.expires_at,
            is_revoked=token.is_revoked,
        )
        await self.session.execute(stmt)

    async def get_by_id(self, token_id: uuid.UUID) -> RefreshToken | None:
        return await self.session.get(RefreshToken, token_id)

    async def revoke(self, token_id: uuid.UUID, now: datetime.datetime) -> None:
        stmt = update(refresh_tokens).where(refresh_tokens.c.id == token_id).values(is_revoked=True)
        await self.session.execute(stmt)

    async def revoke_all_for_user(self, user_id: uuid.UUID, now: datetime.datetime) -> None:
        """Отозвать ВСЕ refresh-токены пользователя (включая активные)."""
        stmt = (
            update(refresh_tokens)
            .where(refresh_tokens.c.user_id == user_id)
            .values(is_revoked=True)
        )
        await self.session.execute(stmt)

    async def update(self, token: RefreshToken) -> None:
        stmt = (
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
            )
        )
        await self.session.execute(stmt)


class SqlAlchemyUsersSubscriptionRepository(ABCUsersSubscriptionRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, user_subscription: UserSubscription) -> None:
        stmt = insert(user_sub_table).values(
            id=user_subscription.id,
            user_id=user_subscription.user_id,
            plan=user_subscription.plan,
            started_at=user_subscription.started_at,
            expires_at=user_subscription.expires_at,
            is_active=user_subscription.is_active,
        )
        await self.session.execute(stmt)

    async def get_by_user_id(self, user_id: uuid.UUID) -> UserSubscription | None:
        result = await self.session.execute(
            select(user_sub_table).where(user_sub_table.c.user_id == user_id),
        )
        row = result.first()
        return self._row_to_user(row) if row else None

    async def get_by_id(self, user_sub_id: uuid.UUID) -> UserSubscription | None:
        result = await self.session.execute(
            select(user_sub_table).where(user_sub_table.c.id == user_sub_id),
        )
        row = result.first()
        return self._row_to_user(row) if row else None

    def _row_to_user(self, row) -> UserSubscription:
        """Конвертирует строку результата SQLAlchemy в доменную модель UserSubscription.

        Args:
            row: Строка результата запроса SQLAlchemy.

        Returns:
                Экземпляр доменной модели UserSubscription.

        Note:
            Внутренний метод, не предназначен для использования извне.

        """
        r = row[0] if isinstance(row, tuple) else row
        return UserSubscription(
            subscription_id=r.id,
            user_id=r.user_id,
            plan=r.plan,
            started_at=r.started_at,
            expires_at=r.expires_at,
            is_active=r.is_active,
        )


class SqlAlchemyUserAuthStateRepository(AbstractUserAuthStateRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_user_id(self, user_id: uuid.UUID) -> UserAuthState | None:
        stmt = select(user_auth_state).where(user_auth_state.c.user_id == user_id)
        result = await self.session.execute(stmt)
        row = result.first()

        if not row:
            return None

        data = row._mapping
        return UserAuthState(
            user_id=data['user_id'],
            failed_attempts=data['failed_attempts'],
            locked_until=data['locked_until'],
            last_failed_at=data['last_failed_at'],
            lock_count=data['lock_count'],
        )

    async def create(self, state: UserAuthState) -> None:
        await self.session.execute(
            insert(user_auth_state).values(
                user_id=state.user_id,
                failed_attempts=state.failed_attempts,
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
                locked_until=state.locked_until,
                last_failed_at=state.last_failed_at,
                lock_count=state.lock_count,
            ),
        )
