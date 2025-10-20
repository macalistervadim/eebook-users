import logging

from src.adapters.orm import metadata
from src.config.loader import SettingsLoader
from src.config.settings import Settings
from src.exceptions import (
    BootstrapInitializationError,
    DatabaseCreateTablesError,
)
from src.infrastructure.database.engine import get_engine
from src.infrastructure.logging.logger import configure_logging

logger = logging.getLogger(__name__)


async def bootstrap() -> Settings:
    try:
        configure_logging()
        await SettingsLoader().load()
        settings = Settings()  # type: ignore
        _ = get_engine()
        logger.info('Bootstrap успешно инициализировал компоненты')
        return settings

    except Exception as e:
        logger.exception('Bootstrap failed')
        raise BootstrapInitializationError(f'Failed to bootstrap application: {str(e)}') from e


async def create_all_tables() -> None:
    engine = get_engine()
    try:
        async with engine.begin() as conn:
            await conn.run_sync(metadata.create_all)
    except Exception as e:
        logger.critical(f'Failed to create database tables: {str(e)}', exc_info=True)
        raise DatabaseCreateTablesError(f'Failed to initialize database: {str(e)}') from e
