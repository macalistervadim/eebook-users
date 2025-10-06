import logging
import os

from src.adapters.interfaces import ISecretsProvider
from src.adapters.vault import VaultClient
from src.exceptions import ConfigurationError

logger = logging.getLogger(__name__)


class SettingsLoader:
    """Загружает секреты из Vault в переменные окружения."""

    def __init__(self, secrets_provider: ISecretsProvider | None = None) -> None:
        try:
            self._sp = secrets_provider or VaultClient()
        except Exception as e:
            raise ConfigurationError(
                f'Failed to initialize secrets provider: {e}',
            ) from e

    async def load(self) -> None:
        """Загружает секреты из Vault в env."""
        secret_paths = [
            'eebook/users',
        ]
        for path in secret_paths:
            data = await self._sp.get_secret(path)
            for key, value in data.items():
                os.environ[key] = str(value)
        logger.info('Secrets loaded from Vault')
