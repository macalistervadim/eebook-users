from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.service_layer.dependencies import get_settings


@lru_cache
def get_engine() -> AsyncEngine:
    """Ленивая инициализация engine. Настройки должны быть загружены до вызова."""
    settings = get_settings()  # type: ignore
    return create_async_engine(
        settings.postgres_uri,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_pre_ping=True,
        pool_recycle=300,
        connect_args={'command_timeout': 10},
    )


@lru_cache
def get_session_factory() -> sessionmaker:
    """Ленивая инициализация session factory."""
    engine = get_engine()
    return sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)  # type: ignore
