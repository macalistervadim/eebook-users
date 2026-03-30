import logging
import json
from typing import Annotated, Any, Literal

from pydantic import field_validator
from pydantic_settings import NoDecode
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

_settings: 'Settings | None' = None


class Settings(BaseSettings):
    """Pydantic-модель конфигурации приложения."""

    SERVICE_NAME: str = 'eebook-users'
    APP_ENV: str = 'dev'
    DEBUG: bool
    FASTAPI_SECRET: str
    JWT_ALGORITHM: Literal['HS256', 'RS256'] = 'HS256'
    JWT_SECRET: str | None = None
    JWT_PRIVATE_KEY: str | None = None
    JWT_PUBLIC_KEY: str | None = None
    ACCESS_TOKEN_TTL_MINUTES: int = 15
    REFRESH_TOKEN_TTL_DAYS: int = 15
    MAX_LOGIN_ATTEMPTS: int = 5
    LOGIN_LOCK_MINUTES: int = 15
    REDIS_URL: str = 'redis://redis:6379/0'
    SUBSCRIPTIONS_SERVICE_URL: str | None = None
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int
    POSTGRES_HOST: str
    CORS_ORIGINS: Annotated[list[str], NoDecode] = ['*']

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='allow',
    )

    @staticmethod
    def _parse_list_env(value: Any) -> Any:
        if isinstance(value, list):
            return value
        if not isinstance(value, str):
            return value

        stripped = value.strip()
        if not stripped:
            return []

        if stripped.startswith('['):
            try:
                parsed = json.loads(stripped)
            except json.JSONDecodeError:
                return [item.strip() for item in stripped.split(',') if item.strip()]
            if isinstance(parsed, list):
                return [str(item).strip() for item in parsed if str(item).strip()]
            return value

        return [item.strip() for item in stripped.split(',') if item.strip()]

    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_list_settings(cls, value: Any) -> Any:
        return cls._parse_list_env(value)

    @field_validator('SUBSCRIPTIONS_SERVICE_URL', mode='before')
    @classmethod
    def parse_optional_service_url(cls, value: Any) -> str | None:
        if value is None:
            return None
        if isinstance(value, str):
            stripped = value.strip()
            return stripped or None
        return str(value)

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
