from typing import Any, Protocol


class ISecretsProvider(Protocol):
    """Контракт для любого хранилища секретов."""

    def get_secrets(self) -> dict[str, Any]:
        """Вернуть набор секретов в виде key-value."""
        ...


class IPasswordHasher(Protocol):
    """Контракт для реализации собственного хэширования и работы с паролями."""

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Проверить переданый пароль с установленным.

        Args:
            password: Введенный пароль
            hashed_password: Захэшированный пароль

        Returns:
            True, если пароль совпадает, False в ином случае

        """
        ...

    def hash_password(self, password: str) -> str:
        """Захэширвать переданный пароль и вернуть его хэш.

        Args:
            password: Пароль, который необходимо захэшировать

        Returns:
            Хэш пароля.

        """
        ...
