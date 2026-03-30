"""ASGI entrypoint for the users service."""

from src.app_factory import bootstrap, create_app


def create_app_sync():
    """Bootstrap infrastructure and build the FastAPI application."""
    settings = bootstrap()
    return create_app(settings)
