import abc

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.domain.exceptions.exceptions import EmailAlreadyRegisteredError, UsernameAlreadyTakenError
from src.infrastructure.database.repository.abc import (
    ABCUsersRepository,
    AbstractEmailVerificationTokenRepository,
    AbstractOutboxEventRepository,
    AbstractRefreshTokenRepository,
    AbstractUserAuthStateRepository,
)
from src.infrastructure.database.repository.factory import (
    ABCEmailVerificationTokenRepositoryFactory,
    ABCOutboxEventRepositoryFactory,
    ABCRefreshTokenRepositoryFactory,
    ABCUserAuthStateRepositoryFactory,
    ABCUsersRepositoryFactory,
)


class AbstractUnitOfWork(abc.ABC):
    users: ABCUsersRepository
    refresh_tokens: AbstractRefreshTokenRepository
    user_auth_state: AbstractUserAuthStateRepository
    email_verification_tokens: AbstractEmailVerificationTokenRepository
    outbox_events: AbstractOutboxEventRepository

    async def __aenter__(self) -> 'AbstractUnitOfWork':
        return self

    async def __aexit__(self, *args) -> None:
        await self.rollback()

    async def commit(self) -> None:
        await self._commit()

    @abc.abstractmethod
    async def _commit(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def rollback(self) -> None:
        raise NotImplementedError


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    UNIQUE_CONSTRAINT_MAP = {
        'users_email_key': EmailAlreadyRegisteredError,
        'users_username_key': UsernameAlreadyTakenError,
        'email_verification_tokens_token_hash_key': RuntimeError,
    }

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        repo_factory: ABCUsersRepositoryFactory,
        refresh_token_repo_factory: ABCRefreshTokenRepositoryFactory,
        user_auth_state_repo_factory: ABCUserAuthStateRepositoryFactory,
        email_verification_token_repo_factory: ABCEmailVerificationTokenRepositoryFactory,
        outbox_event_repo_factory: ABCOutboxEventRepositoryFactory,
    ) -> None:
        self.session_factory = session_factory
        self.repo_factory = repo_factory
        self._refresh_token_repo_factory = refresh_token_repo_factory
        self._user_auth_state_repo_factory = user_auth_state_repo_factory
        self._email_verification_token_repo_factory = email_verification_token_repo_factory
        self._outbox_event_repo_factory = outbox_event_repo_factory

    async def __aenter__(self) -> 'SqlAlchemyUnitOfWork':
        self.session: AsyncSession = self.session_factory()
        self.users = self.repo_factory.create(self.session)
        self.refresh_tokens = self._refresh_token_repo_factory.create(self.session)
        self.user_auth_state = self._user_auth_state_repo_factory.create(self.session)
        self.email_verification_tokens = self._email_verification_token_repo_factory.create(self.session)
        self.outbox_events = self._outbox_event_repo_factory.create(self.session)
        return await super().__aenter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type:
            await self.rollback()
        else:
            await self._commit()
        await self.session.close()

    async def _commit(self) -> None:
        try:
            await self.session.commit()
        except IntegrityError as exc:
            self._handle_integrity_error(exc)
            raise

    def _handle_integrity_error(self, exc: IntegrityError):
        msg = str(exc.orig)
        for constraint, error_cls in self.UNIQUE_CONSTRAINT_MAP.items():
            if constraint in msg:
                raise error_cls()
        raise exc

    async def rollback(self) -> None:
        await self.session.rollback()
