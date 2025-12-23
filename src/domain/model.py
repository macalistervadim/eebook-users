import datetime
import uuid

from src.domain.exceptions.exceptions import (
    EmailAlreadyVerifiedError,
    EmailNotVerifiedError,
    InvalidCredentialsError,
    InvalidEmailError,
    InvalidFirstNameError,
    InvalidLastNameError,
    InvalidUsernameError,
    MaxLoginAttemptsExceeded,
    SameEmailError,
    SamePasswordError,
    UserDisabledError,
)
from src.schemas.internal.role import UserRole
from src.schemas.internal.subscription import SubscriptionPlan


class UserAuthState:
    def __init__(
        self,
        user_id: uuid.UUID,
        failed_attempts: int = 0,
        locked_until: datetime.datetime | None = None,
        last_failed_at: datetime.datetime | None = None,
    ) -> None:
        self.user_id = user_id
        self.failed_attempts = failed_attempts
        self.locked_until = locked_until
        self.last_failed_at = last_failed_at

    def is_locked(self, now: datetime.datetime) -> bool:
        return self.locked_until is not None and self.locked_until > now

    def register_failed_attempt(
        self,
        now: datetime.datetime,
        max_attempts: int,
        lock_time: datetime.timedelta,
    ) -> int:
        if self.locked_until and self.locked_until <= now:
            self.failed_attempts = 0
            self.locked_until = None

        self.failed_attempts += 1
        self.last_failed_at = now

        remaining = max_attempts - self.failed_attempts

        if remaining <= 0:
            self.locked_until = now + lock_time
            raise MaxLoginAttemptsExceeded(
                max_attempts=max_attempts,
                retry_after=lock_time,
            )

        return remaining

    def register_success(self, now: datetime.datetime) -> None:
        self.failed_attempts = 0
        self.locked_until = None


class UserSubscription:
    """Доменная сущность подписки пользователя.

    Не знает ничего о платежах, БД или API.
    Содержит только бизнес-логику валидности.
    """

    def __init__(
        self,
        subscription_id: uuid.UUID,
        user_id: uuid.UUID,
        plan: SubscriptionPlan,
        started_at: datetime.datetime,
        expires_at: datetime.datetime | None,
        is_active: bool,
    ) -> None:
        self.id = subscription_id
        self.user_id = user_id
        self.plan = plan
        self.started_at = started_at
        self.expires_at = expires_at
        self.is_active = is_active

    def is_valid(self, now: datetime.datetime) -> bool:
        """Проверить, активна ли подписка на текущий момент."""
        if not self.is_active:
            return False

        if self.expires_at and self.expires_at <= now:
            return False

        return True


class User:
    """Доменная модель пользователя."""

    def __init__(
        self,
        user_id: uuid.UUID | None,
        first_name: str,
        last_name: str,
        email: str,
        username: str,
        hashed_password: str,
        role: UserRole | None,
        created_at: datetime.datetime,
        updated_at: datetime.datetime,
        last_login_at: datetime.datetime | None,
        is_verified: bool = False,
        is_disabled: bool = False,
    ) -> None:
        if not email:
            raise InvalidEmailError()
        if not first_name:
            raise InvalidFirstNameError()
        if not last_name:
            raise InvalidLastNameError()
        if not username:
            raise InvalidUsernameError()
        if not hashed_password:
            raise InvalidCredentialsError()

        self.id = user_id or uuid.uuid4()
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.email = email.lower().strip()
        self.hashed_password = hashed_password

        self.role = role or UserRole.USER
        self.is_verified = is_verified
        self.is_disabled = is_disabled

        self.created_at = created_at
        self.updated_at = updated_at
        self.last_login_at = last_login_at

    def update_last_login_time(self, now: datetime.datetime) -> None:
        self.last_login_at = now

    def can_login(self) -> None:
        if self.is_disabled:
            raise UserDisabledError()
        if not self.is_verified:
            raise EmailNotVerifiedError()

    def verify_email(self, now: datetime.datetime) -> None:
        if self.is_verified:
            raise EmailAlreadyVerifiedError()
        self.is_verified = True
        self.updated_at = now

    def disable(self, now: datetime.datetime) -> None:
        self.is_disabled = True
        self.updated_at = now

    def enable(self, now: datetime.datetime) -> None:
        self.is_disabled = False
        self.updated_at = now

    def change_password(self, hashed_password: str, now: datetime.datetime) -> None:
        if hashed_password == self.hashed_password:
            raise SamePasswordError()
        self.hashed_password = hashed_password
        self.updated_at = now

    def change_email(self, new_email: str, now: datetime.datetime) -> None:
        if self.email == new_email:
            raise SameEmailError()
        self.email = new_email.lower().strip()
        self.is_verified = False
        self.updated_at = now

    def __str__(self) -> str:
        return f'User - {self.first_name} {self.last_name} ({self.email})'

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'id={self.id!r}, '
            f'first_name={self.first_name!r}, '
            f'last_name={self.last_name!r}, '
            f'email={self.email!r}, '
            f'username={self.username!r}, '
            f'hashed_password={self.hashed_password}, '
            f'is_disabled={self.is_disabled!r}, '
            f'role={self.role!r}, '
            f'is_verified={self.is_verified!r}, '
            f'created_at={self.created_at!r}, '
            f'updated_at={self.updated_at!r}, '
            f'last_login_at={self.last_login_at!r})'
        )
