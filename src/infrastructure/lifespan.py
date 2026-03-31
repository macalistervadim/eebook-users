import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.config.settings import get_settings
from src.infrastructure.database.engine import get_engine
from src.infrastructure.messaging.rabbit import RabbitOutboxRelaySupervisor

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    relay_supervisor: RabbitOutboxRelaySupervisor | None = None

    if settings.RABBITMQ_URL:
        relay_supervisor = RabbitOutboxRelaySupervisor(
            url=settings.RABBITMQ_URL,
            exchange_name=settings.RABBITMQ_EXCHANGE,
        )
        await relay_supervisor.start()

    try:
        yield
    finally:
        if relay_supervisor is not None:
            await relay_supervisor.stop()
        engine = get_engine()
        await engine.dispose()
