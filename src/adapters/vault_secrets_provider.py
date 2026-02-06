from typing import Any

from src.adapters.interfaces import ISecretsProvider
from src.adapters.vault import VaultClient


class VaultSecretsProvider(ISecretsProvider):
    def __init__(self, client: VaultClient, secret_paths: list[str]):
        self._client = client
        self._paths = secret_paths

    def get_secrets(self) -> dict[str, Any]:
        result: dict[str, Any] = {}

        for path in self._paths:
            data = self._client.get_secret(path)

            if not isinstance(data, dict):
                raise TypeError(
                    f'Vault secret at "{path}" must be a dict, got {type(data)}',
                )

            for k, v in data.items():
                result[k] = v

        return result
