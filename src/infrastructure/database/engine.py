import logging
from functools import lru_cache

import sqlalchemy.exc as sa_exceptions
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.infrastructure.database.exceptions import (
    DatabaseArgumentError,
    DatabaseConnectionError,
    DatabaseTimeoutError,
)
from src.service_layer.dependencies import get_settings

logger = logging.getLogger(__name__)


@lru_cache
def get_engine() -> AsyncEngine:
    """Ленивая инициализация engine. Настройки должны быть загружены до вызова.

    Returns:
        AsyncEngine: Инициализированный асинхронный движок SQLAlchemy

    Raises:
        DatabaseConnectionError: Если не удалось создать подключение к БД

    """
    settings = get_settings()

    if not settings.postgres_uri:
        error_msg = 'Не указан URI подключения к PostgreSQL в настройках'
        logger.critical(error_msg)
        raise DatabaseConnectionError(error_msg)

    try:
        engine = create_async_engine(
            settings.postgres_uri,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_pre_ping=True,
            pool_recycle=300,
            connect_args={'command_timeout': 10},
        )
        logger.info('Асинхронный движок БД успешно создан')
        return engine

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


@lru_cache
def get_session_factory() -> sessionmaker:
    """Ленивая инициализация session factory."""
    engine = get_engine()
    return sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)  # type: ignore
