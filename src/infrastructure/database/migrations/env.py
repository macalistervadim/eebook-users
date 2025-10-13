import asyncio
from logging.config import fileConfig
from sqlalchemy import pool, create_engine
from alembic import context

from src.adapters.orm import metadata
from src.config.loader import SettingsLoader
from src.service_layer.dependencies import get_settings

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = metadata


async def init_settings_and_get_uri() -> str:
    """Подгружает секреты из Vault и возвращает PostgreSQL URI."""
    loader = SettingsLoader()
    await loader.load()
    settings = get_settings()
    # Alembic не поддерживает async драйвер, поэтому убираем "+asyncpg"
    return settings.postgres_uri.replace('+asyncpg', '')


def get_sync_uri() -> str:
    """Обертка для асинхронной функции, чтобы можно было вызвать в sync-коде."""
    return asyncio.get_event_loop().run_until_complete(init_settings_and_get_uri())


def run_migrations_offline():
    url = get_sync_uri()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={'paramstyle': 'named'},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    uri = get_sync_uri()
    connectable = create_engine(uri, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
