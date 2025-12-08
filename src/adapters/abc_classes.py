import abc
import datetime
import uuid

from src.domain.model import User
from src.schemas.api.auth import TokenPair
from src.schemas.internal.auth import RefreshToken
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


class ABCAuthService(abc.ABC):
    """Абстракция сервиса аутентификации и управления JWT-токенами.

    Сервис отвечает за:
    - генерацию пары access/refresh токенов,
    - проверку access-токена,
    - ротацию refresh-токенов,
    - отзыв refresh-токенов по ID,
    - обновление токенов с проверкой fingerprint.
    """

    @abc.abstractmethod
    async def create_token_pair(
        self,
        uow: AbstractUnitOfWork,
        user_id: uuid.UUID,
        fingerprint: str,
    ) -> TokenPair:
        """Создать новую пару access + refresh токенов и сохранить refresh в БД.

        Args:
            uow (AbstractUnitOfWork): Контекст работы с БД.
            user_id (uuid.UUID): ID пользователя.
            fingerprint (str): Отпечаток клиентского устройства (ip + ua).

        Returns:
            TokenPair: Новая пара токенов (access_token + refresh_token ID).

        """

    @abc.abstractmethod
    async def validate_access_token(self, token: str):
        """Проверить валидность access-токена.

        Args:
            token (str): Access JWT.

        Returns:
            dict: Payload токена при успешной валидации, или None.

        """
        ...

    @abc.abstractmethod
    async def refresh_tokens(
        self,
        uow: AbstractUnitOfWork,
        refresh_token_id: str,
        current_fingerprint: str,
    ) -> TokenPair | None:
        """Обновить токены по ID refresh-токена (opaque refresh) с проверкой fingerprint.

        Args:
            uow (AbstractUnitOfWork): Контекст работы с БД.
            refresh_token_id (str): ID refresh-токена (из куки).
            current_fingerprint (str): Отпечаток текущего клиента (ip + ua).

        Returns:
            TokenPair | None: Новая пара токенов или None, если refresh недействителен.

        """
        ...

    @abc.abstractmethod
    async def revoke_by_id(
        self,
        uow: AbstractUnitOfWork,
        refresh_token_id: uuid.UUID,
    ) -> bool:
        """Отозвать refresh-токен по ID (например, при logout).

        Args:
            uow (AbstractUnitOfWork): Контекст работы с БД.
            refresh_token_id (uuid.UUID): ID refresh-токена.

        Returns:
            bool: True при успешном отзыве токена, False если токен не найден или уже отозван.

        """
        ...


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
