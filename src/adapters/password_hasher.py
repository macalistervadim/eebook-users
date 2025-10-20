from passlib.hash import argon2

from src.adapters.interfaces import IPasswordHasher


class UserPasswordHasher(IPasswordHasher):
    """Рабочий хешер паролей пользователей с использованием Argon2."""

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Проверяет соответствие пароля и его хеша.

        Args:
            password: Оригинальный пароль в открытом виде.
            hashed_password: Хеш пароля для проверки.

        Returns:
            True, если пароль совпадает, иначе False.

        """
        return argon2.verify(password, hashed_password)

    def hash_password(self, password: str) -> str:
        """Создает безопасный хеш для указанного пароля.

        Args:
            password: Пароль в открытом виде.

        Returns:
            Хешированное значение пароля.

        """
        return argon2.hash(password)
