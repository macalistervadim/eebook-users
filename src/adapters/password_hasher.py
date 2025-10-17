from passlib.hash import argon2

from src.adapters.interfaces import IPasswordHasher


class UserPasswordHasher(IPasswordHasher):
    """Рабочий хешер паролей пользователей с использованием Argon2."""

    def verify_password(self, password: str, hashed_password: str) -> bool:
        return argon2.verify(password, hashed_password)

    def hash_password(self, password: str) -> str:
        return argon2.hash(password)
