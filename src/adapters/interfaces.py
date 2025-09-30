from typing import Any, Protocol


class ISecretsProvider(Protocol):
    """
    Контракт для любого хранилища секретов.
    """

    def read_secret(self, path: str) -> dict[str, Any]:
        """Вернуть словарь данных секрета по пути"""
