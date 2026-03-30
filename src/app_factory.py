"""Bootstrap and FastAPI app factory for the users service."""

import logging

from fastapi import FastAPI

from src.config.settings import Settings, setup_settings
from src.exceptions import BootstrapInitializationError
from src.infrastructure.database.engine import init_engine_and_session
from src.infrastructure.database.orm import start_mappers
from src.infrastructure.lifespan import lifespan
from src.infrastructure.logging.logger import configure_logging
from src.infrastructure.middleware.cors import setup_cors
from src.infrastructure.middleware.request_context import setup_request_context
from src.interfaces.api import endpoints
from src.interfaces.api.exception_handlers import setup_exception_handlers

logger = logging.getLogger(__name__)


def bootstrap() -> Settings:
    try:
        settings = Settings()
        configure_logging(level='DEBUG' if settings.DEBUG else 'INFO')
        setup_settings(settings)
        start_mappers()
        init_engine_and_session()
        return settings
    except Exception as exc:
        logger.exception('Bootstrap failed')
        raise BootstrapInitializationError(f'Failed to bootstrap application: {exc}') from exc


def create_app(*args, **kwargs) -> FastAPI:
    """Build the FastAPI application."""
    app = FastAPI(
        title='eebook-users',
        description='Users service for authentication, registration and user profiles',
        version='0.1.0',
        docs_url='/api/docs',
        redoc_url='/api/redoc',
        openapi_url='/api/openapi.json',
        lifespan=lifespan,
    )

    setup_request_context(app)
    setup_cors(app)
    setup_exception_handlers(app)
    app.include_router(endpoints.router)
    return app
