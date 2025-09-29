from sqlalchemy.ext.asyncio import create_async_engine

from src.adapters.orm import metadata, start_mappers
from src.config import Settings, SettingsLoader, get_postgres_uri


async def create_all_tables(database_url: str):
    engine = create_async_engine(database_url)
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    await engine.dispose()


def bootstrap():
    """
    Синхронная часть инфраструктурной инициализации (секреты, настройки, мапперы).
    Возвращает settings.
    """
    SettingsLoader().load()
    settings = Settings()  # type: ignore
    start_mappers()
    return settings


async def async_bootstrap(settings):
    """
    Асинхронная часть инфраструктурной инициализации (создание таблиц).
    """
    await create_all_tables(get_postgres_uri())
