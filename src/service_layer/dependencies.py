import logging
from functools import lru_cache

from src.config.settings import Settings

logger = logging.getLogger(__name__)


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore
