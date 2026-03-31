import abc
import datetime
import uuid

from src.domain.model import EmailVerificationToken, OutboxEvent, User, UserAuthState
from src.schemas.internal.auth import RefreshToken


class ABCUsersRepository(abc.ABC):
    @abc.abstractmethod
    async def add(self, user: User) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_by_username(self, username: str) -> User | None:
        raise NotImplementedError

    @abc.abstractmethod
    async def update(self, user: User) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def remove(self, user_id: uuid.UUID) -> None:
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


class AbstractUserAuthStateRepository(abc.ABC):
    @abc.abstractmethod
    async def get_by_user_id(self, user_id: uuid.UUID) -> UserAuthState | None:
        raise NotImplementedError

    @abc.abstractmethod
    async def create(self, state: UserAuthState) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def save(self, state: UserAuthState) -> None:
        raise NotImplementedError


class AbstractEmailVerificationTokenRepository(abc.ABC):
    @abc.abstractmethod
    async def add(self, token: EmailVerificationToken) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_active_by_token_hash(self, token_hash: str) -> EmailVerificationToken | None:
        raise NotImplementedError

    @abc.abstractmethod
    async def revoke_active_for_user(self, user_id: uuid.UUID, now: datetime.datetime) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def save(self, token: EmailVerificationToken) -> None:
        raise NotImplementedError


class AbstractOutboxEventRepository(abc.ABC):
    @abc.abstractmethod
    async def add(self, event: OutboxEvent) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def list_pending(self, limit: int) -> list[OutboxEvent]:
        raise NotImplementedError

    @abc.abstractmethod
    async def save(self, event: OutboxEvent) -> None:
        raise NotImplementedError
