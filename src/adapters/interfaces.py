from typing import Any, Protocol


class ISecretsProvider(Protocol):
    """
    Контракт для любого хранилища секретов.
    """

    async def get_secret(self, path: str, key: str | None = None) -> dict[str, Any]:
        """
        Получить значение секрета по пути и ключу.

        Args:
            path: Путь к секрету в хранилище
            key: Ключ секрета

        Returns:
            Значение секрета или None, если не найдено
        """
        ...
