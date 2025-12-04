import logging

import sqlalchemy.exc as sa_exceptions
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.config.settings import get_settings
from src.infrastructure.database.exceptions import (
    DatabaseArgumentError,
    DatabaseConnectionError,
    DatabaseTimeoutError,
)

logger = logging.getLogger(__name__)

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker | None = None


def init_engine_and_session() -> None:
    global _engine, _session_factory
    if _engine is not None:
        raise RuntimeError('Engine already initialized')

    settings = get_settings()
    try:
        _engine = create_async_engine(
            settings.postgres_uri,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_pre_ping=True,
            pool_recycle=300,
            connect_args={'command_timeout': 10},
        )
        _session_factory = async_sessionmaker(
            bind=_engine,
            expire_on_commit=False,
        )
        logger.info('Асинхронный движок и session factory успешно созданы')
    except sa_exceptions.TimeoutError as e:
        logger.exception('Таймаут подключения к БД')
        raise DatabaseTimeoutError(f'Таймаут подключения к БД: {str(e)}') from e
    except sa_exceptions.ArgumentError as e:
        logger.exception('Некорректные параметры подключения к БД:')
        raise DatabaseArgumentError(f'Некорректные параметры подключения к БД: {str(e)}') from e
    except sa_exceptions.SQLAlchemyError as e:
        logger.exception('Ошибка SQLAlchemy при создании движка')
        raise DatabaseConnectionError(f'Ошибка SQLAlchemy при создании движка: {str(e)}') from e
    except Exception as e:
        error_msg = f'Непредвиденная ошибка при создании движка БД: {str(e)}'
        logger.critical(error_msg, exc_info=True)
        raise DatabaseConnectionError(error_msg) from e


def get_engine() -> AsyncEngine:
    if _engine is None:
        raise RuntimeError('Engine not initialized. Call init_engine_and_session() first.')
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    if _session_factory is None:
        raise RuntimeError('Session factory not initialized.')
    return _session_factory
