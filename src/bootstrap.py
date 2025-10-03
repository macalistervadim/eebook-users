import logging

from src.adapters.orm import metadata
from src.config.loader import SettingsLoader
from src.config.settings import Settings
from src.exceptions import ConfigurationError, DatabaseError
from src.infrastructure.database.engine import get_engine

logger = logging.getLogger(__name__)


async def bootstrap() -> Settings:
    try:
        await SettingsLoader().load()
        settings = Settings()  # type: ignore
        _ = get_engine()
        await create_all_tables()
        return settings

    except Exception as e:
        logger.error(f'Bootstrap failed: {str(e)}', exc_info=True)
        raise ConfigurationError(f'Failed to bootstrap application: {str(e)}') from e


async def create_all_tables():
    engine = get_engine()
    try:
        async with engine.begin() as conn:
            await conn.run_sync(metadata.create_all)
    except Exception as e:
        logger.error(f'Failed to create database tables: {str(e)}', exc_info=True)
        raise DatabaseError(f'Failed to initialize database: {str(e)}') from e
