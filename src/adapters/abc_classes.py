import abc
import datetime
import uuid
from collections.abc import Awaitable


class ABCTimeProvider(abc.ABC):
    @abc.abstractmethod
    def now(self) -> datetime.datetime:
        """Возвращает текущее время в UTC."""
        raise NotImplementedError


class ABCTokenStore(abc.ABC):
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
