import datetime
import uuid

from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.abc_repository import ABCUsersRepository, AbstractRefreshTokenRepository
from src.adapters.orm import refresh_tokens, users
from src.domain.model import User
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
            hashed_password=user.hashed_password,
            is_active=user.is_active,
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

    async def list_all(self, *, only_active: bool = False) -> list[User]:
        stmt = select(users)
        if only_active:
            stmt = stmt.where(users.c.is_active.is_(True))
        result = await self.session.execute(stmt)
        return [self._row_to_user(row) for row in result.fetchall()]

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
                is_active=user.is_active,
                is_verified=user.is_verified,
                updated_at=user.updated_at,
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
            is_active=r.is_active,
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
