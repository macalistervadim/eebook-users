import logging

from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)

_settings: 'Settings | None' = None


class Settings(BaseSettings):
    """Pydantic-модель конфигурации приложения."""

    FASTAPI_SECRET: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int
    POSTGRES_HOST: str
    CORS_ORIGINS: str

    class Config:
        env_file_encoding = 'utf-8'
        extra = 'allow'

    @property
    def postgres_uri(self) -> str:
        return (
            f'postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}'
            f'@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}'
        )


def setup_settings(settings: Settings) -> None:
    global _settings
    if _settings is not None:
        logger.warning('Settings already initialized — overwriting')
    _settings = settings


def get_settings() -> Settings:
    if _settings is None:
        raise RuntimeError('Settings not initialized yet')
    return _settings
