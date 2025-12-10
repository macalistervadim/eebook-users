import abc
import datetime
import uuid

from src.domain.model import User
from src.schemas.internal.auth import RefreshToken


class ABCUsersRepository(abc.ABC):
    """Абстрактный базовый класс для репозитория пользователей.

    Определяет интерфейс для работы с хранилищем пользователей,
    который должен быть реализован в конкретных классах-наследниках.
    """

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


class AbstractRefreshTokenRepository(abc.ABC):
    @abc.abstractmethod
    async def add(self, token: RefreshToken) -> None: ...

    @abc.abstractmethod
    async def get_by_id(self, token_id: uuid.UUID) -> RefreshToken | None: ...

    @abc.abstractmethod
    async def update(self, token: RefreshToken) -> None: ...

    @abc.abstractmethod
    async def revoke(self, token_id: uuid.UUID, now: datetime.datetime) -> None: ...

    @abc.abstractmethod
    async def revoke_all_for_user(self, user_id: uuid.UUID, now: datetime.datetime) -> None: ...
