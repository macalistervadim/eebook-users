import datetime
import uuid


class User:
    def __init__(
        self,
        user_id: uuid.UUID | None,
        first_name: str,
        last_name: str,
        email: str,
        username: str,
        hashed_password: str,
        created_at: datetime.datetime,
        updated_at: datetime.datetime,
        last_login_at: datetime.datetime,
        is_active: bool = True,
        is_verified: bool = False,
    ) -> None:
        self.id = user_id or uuid.uuid4()
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.email = email
        self.hashed_password = hashed_password
        self.is_active = is_active
        self.is_verified = is_verified
        self.created_at = created_at
        self.updated_at = updated_at
        self.last_login_at = last_login_at

    def update_login_time(self, now: datetime.datetime) -> None:
        """Обновить время последнего входа."""
        self.last_login_at = now

    def activate(self, now: datetime.datetime) -> None:
        self.is_active = True
        self.updated_at = now

    def deactivate(self, now: datetime.datetime) -> None:
        self.is_active = False
        self.updated_at = now

    def verify_email(self, now: datetime.datetime) -> None:
        self.is_verified = True
        self.updated_at = now

    def change_password(self, hashed_password: str, now: datetime.datetime) -> None:
        """Изменить пароль пользователя."""
        self.hashed_password = hashed_password
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
            f'is_active={self.is_active!r}, '
            f'is_verified={self.is_verified!r}, '
            f'created_at={self.created_at!r}, '
            f'updated_at={self.updated_at!r}, '
            f'last_login_at={self.last_login_at!r})'
        )
