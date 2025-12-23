import abc
import datetime
import uuid

from src.schemas.api.auth import TokenPair
from src.service_layer.uow import AbstractUnitOfWork


class ABCTimeProvider(abc.ABC):
    @abc.abstractmethod
    def now(self) -> datetime.datetime:
        """Возвращает текущее время в UTC."""
        raise NotImplementedError


class ABCTokenStore(abc.ABC):
    """Абстракция хранилища отозванных JWT (blacklist)."""

    @abc.abstractmethod
    async def revoke(self, jti: str, expire_in: datetime.timedelta) -> None:
        """Отозвать токен.

        Args:
            jti: Уникальный идентификатор токена.
            expire_in: Через сколько времени запись должна исчезнуть.

        """
        ...

    @abc.abstractmethod
    async def is_revoked(self, jti: str) -> bool:
        """Проверить, отозван ли токен.

        Args:
            jti: Идентификатор токена.

        Returns:
            bool: True, если токен был отозван.

        """
        ...
