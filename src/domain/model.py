import datetime
import uuid

from src.adapters.interfaces import IPasswordHasher


class User:
    def __init__(
        self,
        user_id: uuid.UUID | None,
        first_name: str,
        last_name: str,
        email: str,
        username: str,
        hashed_password: str,
        _hasher: IPasswordHasher,
        is_active: bool = True,
        is_verified: bool = False,
        created_at: datetime.datetime | None = None,
        updated_at: datetime.datetime | None = None,
        last_login_at: datetime.datetime | None = None,
    ) -> None:
        self.id = user_id or uuid.uuid4()
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.email = email
        self.hashed_password = hashed_password
        self.is_active = is_active
        self.is_verified = is_verified
        self._hasher = _hasher

        now = datetime.datetime.now(datetime.UTC)
        self.created_at = created_at or now
        self.updated_at = updated_at or now
        self.last_login_at = last_login_at

    def update_login_time(self) -> None:
        """Обновить время последнего входа."""
        self.last_login_at = datetime.datetime.now(datetime.UTC)

    def activate(self) -> None:
        self.is_active = True
        self.updated_at = datetime.datetime.now(datetime.UTC)

    def deactivate(self) -> None:
        self.is_active = False
        self.updated_at = datetime.datetime.now(datetime.UTC)

    def verify_email(self) -> None:
        self.is_verified = True
        self.updated_at = datetime.datetime.now(datetime.UTC)

    def verify_password(self, password: str) -> bool:
        return self._hasher.verify_password(password, self.hashed_password)

    def set_password(self, password: str) -> None:
        self.hashed_password = self._hasher.hash_password(password)

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
            f'_hasher={self._hasher!r}, '
            f'is_active={self.is_active!r}, '
            f'is_verified={self.is_verified!r}, '
            f'created_at={self.created_at!r}, '
            f'updated_at={self.updated_at!r}, '
            f'last_login_at={self.last_login_at!r})'
        )
