import logging
import os

from src.adapters.orm import start_mappers
from src.adapters.vault import VaultClient
from src.adapters.vault_secrets_provider import VaultSecretsProvider
from src.config.settings import Settings, setup_settings
from src.exceptions import (
    BootstrapInitializationError,
)
from src.infrastructure.database.engine import init_engine_and_session
from src.infrastructure.logging.logger import configure_logging

logger = logging.getLogger(__name__)


def bootstrap() -> Settings:
    try:
        env = os.getenv('APP_ENV', 'local')

        configure_logging(level='DEBUG' if env == 'local' else 'INFO')

        if env == 'local':
            settings = Settings()
        elif env == 'prod':
            provider = VaultSecretsProvider(client=VaultClient(), secret_paths=['eebook/users'])
            secrets = provider.get_secrets()
            settings = Settings(**secrets)
        else:
            raise BootstrapInitializationError(f'Unknown APP_ENV: {env}')

        setup_settings(settings)
        start_mappers()
        init_engine_and_session()

        logger.info('Bootstrap успешно инициализировал компоненты')
        return settings
    except Exception as e:
        logger.exception('Bootstrap failed')
        raise BootstrapInitializationError(
            f'Failed to bootstrap application: {str(e)}',
        ) from e
