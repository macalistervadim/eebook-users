import logging

from src.adapters.orm import metadata
from src.config.loader import SettingsLoader
from src.config.settings import Settings, setup_settings
from src.exceptions import (
    BootstrapInitializationError,
    DatabaseCreateTablesError,
)
from src.infrastructure.database.engine import get_engine, init_engine_and_session
from src.infrastructure.logging.logger import configure_logging

logger = logging.getLogger(__name__)


def bootstrap() -> Settings:
    try:
        configure_logging()
        loader = SettingsLoader()
        loader.load()  # загружаем env / секреты
        settings = Settings()  # создаём Pydantic объект
        setup_settings(settings)

        init_engine_and_session()
        logger.info('Bootstrap успешно инициализировал компоненты')
        return settings
    except Exception as e:
        logger.exception('Bootstrap failed')
        raise BootstrapInitializationError(
            f'Failed to bootstrap application: {str(e)}',
        ) from e


async def create_all_tables() -> None:
    engine = get_engine()
    try:
        async with engine.begin() as conn:
            await conn.run_sync(metadata.create_all)
    except Exception as e:
        logger.critical(f'Failed to create database tables: {str(e)}', exc_info=True)
        raise DatabaseCreateTablesError(f'Failed to initialize database: {str(e)}') from e
