import abc
import datetime
import uuid

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.interfaces import IPasswordHasher
from src.adapters.orm import users
from src.domain.model import User


class ABCUsersRepository(abc.ABC):
    """Абстрактный базовый класс для репозитория пользователей.

    Определяет интерфейс для работы с хранилищем пользователей,
    который должен быть реализован в конкретных классах-наследниках.
    """

    @abc.abstractmethod
    async def update_login_time(self, user_id: uuid.UUID) -> None:
        """Обновить время последнего входа пользователя.

        Args:
            user_id: Уникальный идентификатор пользователя.

        Raises:
            NotImplementedError: Если метод не переопределен в подклассе.

        """
        raise NotImplementedError

    @abc.abstractmethod
    async def activate(self, user_id: uuid.UUID) -> None:
        """Активировать пользователя.

        Args:
            user_id: Уникальный идентификатор пользователя.

        Raises:
            NotImplementedError: Если метод не переопределен в подклассе.

        """
        raise NotImplementedError

    @abc.abstractmethod
    async def deactivate(self, user_id: uuid.UUID) -> None:
        """Деактивировать пользователя.

        Args:
            user_id: Уникальный идентификатор пользователя.

        Raises:
            NotImplementedError: Если метод не переопределен в подклассе.

        """
        raise NotImplementedError

    @abc.abstractmethod
    async def verify_email(self, user_id: uuid.UUID) -> None:
        """Подтвердить email пользователя.

        Args:
            user_id: Уникальный идентификатор пользователя.

        Raises:
            NotImplementedError: Если метод не переопределен в подклассе.

        """
        raise NotImplementedError

    @abc.abstractmethod
    async def verify_password(self, user_id: uuid.UUID, password: str) -> bool:
        """Проверяет корректность пароля пользователя.

        Args:
            user_id: Уникальный идентификатор пользователя.
            password: Пароль для проверки.

        Returns:
            bool: True, если пароль верный, иначе False.

        Raises:
            NotImplementedError: Если метод не переопределен в подклассе.

        """
        raise NotImplementedError

    @abc.abstractmethod
    async def set_password(self, user_id: uuid.UUID, password: str) -> None:
        """Устанавливает новый пароль для пользователя.

        Args:
            user_id: Уникальный идентификатор пользователя.
            password: Новый пароль.

        Raises:
            NotImplementedError: Если метод не переопределен в подклассе.

        """
        raise NotImplementedError

    @abc.abstractmethod
    async def add(self, user: User) -> None:
        """Добавляет пользователя в репозиторий.

        Args:
            user: Объект пользователя для добавления.

        Raises:
            NotImplementedError: Если метод не переопределен в подклассе.

        """
        raise NotImplementedError

    @abc.abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        """Находит пользователя по email.

        Args:
            email: Email пользователя для поиска.

        Returns:
            User | None: Объект пользователя, если найден, иначе None.

        Raises:
            NotImplementedError: Если метод не переопределен в подклассе.

        """
        raise NotImplementedError

    @abc.abstractmethod
    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        """Находит пользователя по уникальному идентификатору.

        Args:
            user_id: UUID пользователя для поиска.

        Returns:
            User | None: Объект пользователя, если найден, иначе None.

        Raises:
            NotImplementedError: Если метод не переопределен в подклассе.

        """
        raise NotImplementedError

    @abc.abstractmethod
    async def get_by_username(self, username: str) -> User | None:
        """Находит пользователя по username.

        Args:
            username: Username пользователя для поиска.

        Returns:
            User | None: Объект пользователя, если найден, иначе None.

        Raises:
            NotImplementedError: Если метод не переопределен в подклассе.

        """
        raise NotImplementedError

    @abc.abstractmethod
    async def list_all(self, *, only_active: bool = False) -> list[User]:
        """Возвращает список всех пользователей.

        Args:
            only_active: Если True, возвращает только активных пользователей.

        Returns:
            list[User]: Список пользователей.

        Raises:
            NotImplementedError: Если метод не переопределен в подклассе.

        """
        raise NotImplementedError

    @abc.abstractmethod
    async def update(self, user: User) -> None:
        """Обновляет данные пользователя в репозитории.

        Args:
            user: Объект пользователя с обновлёнными данными.

        Raises:
            NotImplementedError: Если метод не переопределен в подклассе.

        """
        raise NotImplementedError

    @abc.abstractmethod
    async def remove(self, user_id: uuid.UUID) -> None:
        """Удаляет пользователя из репозитория.

        Args:
            user_id: UUID пользователя для удаления.

        Raises:
            NotImplementedError: Если метод не переопределен в подклассе.

        """
        raise NotImplementedError


class SQLAlchemyUsersRepository(ABCUsersRepository):
    """Реализация репозитория пользователей на SQLAlchemy (PostgreSQL, async) с поддержкой UoW."""

    def __init__(self, session: AsyncSession, hasher: IPasswordHasher):
        self.session = session
        self._hasher = hasher

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
                updated_at=datetime.datetime.now(datetime.UTC),
                last_login_at=user.last_login_at,
            )
        )
        await self.session.execute(stmt)

    async def remove(self, user_id: uuid.UUID) -> None:
        stmt = delete(users).where(users.c.id == user_id)
        await self.session.execute(stmt)

    async def update_login_time(self, user_id: uuid.UUID) -> None:
        stmt = (
            update(users)
            .where(users.c.id == user_id)
            .values(
                last_login_at=datetime.datetime.now(datetime.UTC),
                updated_at=datetime.datetime.now(datetime.UTC),
            )
        )
        await self.session.execute(stmt)

    async def activate(self, user_id: uuid.UUID) -> None:
        stmt = (
            update(users)
            .where(users.c.id == user_id)
            .values(
                is_active=True,
                updated_at=datetime.datetime.now(datetime.UTC),
            )
        )
        await self.session.execute(stmt)

    async def deactivate(self, user_id: uuid.UUID) -> None:
        stmt = (
            update(users)
            .where(users.c.id == user_id)
            .values(
                is_active=False,
                updated_at=datetime.datetime.now(datetime.UTC),
            )
        )
        await self.session.execute(stmt)

    async def verify_email(self, user_id: uuid.UUID) -> None:
        stmt = (
            update(users)
            .where(users.c.id == user_id)
            .values(
                is_verified=True,
                updated_at=datetime.datetime.now(datetime.UTC),
            )
        )
        await self.session.execute(stmt)

    async def verify_password(self, user_id: uuid.UUID, password: str) -> bool:
        user = await self.get_by_id(user_id)
        if not user:
            return False
        return self._hasher.verify_password(password, user.hashed_password)

    async def set_password(self, user_id: uuid.UUID, password: str) -> None:
        hashed = self._hasher.hash_password(password)
        stmt = (
            update(users)
            .where(users.c.id == user_id)
            .values(
                hashed_password=hashed,
                updated_at=datetime.datetime.now(datetime.UTC),
            )
        )
        await self.session.execute(stmt)

    def _row_to_user(self, row) -> User:
        """Конвертирует SQLAlchemy row в доменную модель User."""
        r = row[0] if isinstance(row, tuple) else row
        return User(
            user_id=r.id,
            first_name=r.first_name,
            last_name=r.last_name,
            email=r.email,
            username=r.username,
            hashed_password=r.hashed_password,
            _hasher=self._hasher,
            is_active=r.is_active,
            is_verified=r.is_verified,
            created_at=r.created_at,
            updated_at=r.updated_at,
            last_login_at=r.last_login_at,
        )
