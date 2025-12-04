import logging
import os

from src.adapters.interfaces import ISecretsProvider
from src.adapters.vault import VaultClient
from src.config.exceptions import SettingsLoaderInitializationError

logger = logging.getLogger(__name__)


class SettingsLoader:
    """Загружает секреты из хранилища секретов в переменные окружения."""

    def __init__(self, secrets_provider: ISecretsProvider | None = None) -> None:
        try:
            self._sp = secrets_provider or VaultClient()
            logger.info(f'{SettingsLoader.__name__} успешно инициализирован')
        except Exception as e:
            logger.exception(f'Ошибка при инициализации {SettingsLoader.__name__}')
            raise SettingsLoaderInitializationError(
                f'Ошибка при инициализации {SettingsLoader.__name__}: {e}',
            ) from e

    def load(self) -> None:
        """Загружает секреты из хранилища секретов в env."""
        secret_paths = [
            'eebook/users',
        ]
        for path in secret_paths:
            data = self._sp.get_secret(path)
            for key, value in data.items():
                os.environ[key] = str(value)
        logger.info('Секреты успешно загружены в окружение')
