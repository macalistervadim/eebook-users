import logging
import os

from src.adapters.interfaces import ISecretsProvider

logger = logging.getLogger(__name__)


class SettingsLoader:
    """Загружает секреты из хранилища секретов в переменные окружения."""

    def __init__(self, secrets_provider: ISecretsProvider) -> None:
        self._provider = secrets_provider

    def load(self) -> None:
        """Загружает секреты из хранилища секретов в env."""
        secrets = self._provider.get_secrets()
        for k, v in secrets.items():
            os.environ[k] = v
        logger.info('Секреты успешно загружены в окружение')
