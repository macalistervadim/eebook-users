import abc
import datetime
import uuid
from collections.abc import Awaitable
from typing import Any, Protocol


class ISecretsProvider(Protocol):
    """Контракт для любого хранилища секретов."""

    async def get_secret(self, path: str, key: str | None = None) -> dict[str, Any]:
        """Получить значение секрета по пути и ключу.

        Args:
            path: Путь к секрету в хранилище
            key: Ключ секрета (опционально)

        Returns:
            Значение секрета или None, если не найдено

        """
        ...


class IPasswordHasher(Protocol):
    """Контракт для реализации собственного хэширования и работы с паролями."""

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Проверить переданый пароль с установленным.

        Args:
            password: Введенный пароль
            hashed_password: Захэшированный пароль

        Returns:
            True, если пароль совпадает, False в ином случае

        """
        ...

    def hash_password(self, password: str) -> str:
        """Захэширвать переданный пароль и вернуть его хэш.

        Args:
            password: Пароль, который необходимо захэшировать

        Returns:
            Хэш пароля.

        """
        ...


class AbstractTimeProvider(abc.ABC):
    @abc.abstractmethod
    def now(self) -> datetime.datetime:
        """Возвращает текущее время в UTC."""
        raise NotImplementedError


class AbstractTokenStore(abc.ABC):
    """Абстракция хранилища отозванных JWT (blacklist)."""

    @abc.abstractmethod
    async def revoke(self, jti: str, expire_in: datetime.timedelta) -> Awaitable[None]:
        """Отозвать токен.

        Args:
            jti: Уникальный идентификатор токена.
            expire_in: Через сколько времени запись должна исчезнуть.

        """
        ...

    @abc.abstractmethod
    async def is_revoked(self, jti: str) -> Awaitable[bool]:
        """Проверить, отозван ли токен.

        Args:
            jti: Идентификатор токена.

        Returns:
            bool: True, если токен был отозван.

        """
        ...


class ABCAuthService(abc.ABC):
    """Абстракция сервиса аутентификации."""

    @abc.abstractmethod
    def create_token_pair(self, user_id: uuid.UUID):
        """Создать пару access + refresh токенов."""
        ...

    @abc.abstractmethod
    async def validate_access_token(self, token: str):
        """Проверить access-токен."""
        ...

    @abc.abstractmethod
    async def refresh_token_pair(self, refresh_token: str):
        """Выдать новую пару токенов по refresh-токену."""
        ...

    @abc.abstractmethod
    async def revoke_token_pair(self, access_token: str, refresh_token: str):
        """Отозвать оба токена (logout)."""
        ...
