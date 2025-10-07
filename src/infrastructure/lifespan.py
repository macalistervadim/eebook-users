import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.bootstrap import bootstrap
from src.infrastructure.database.engine import get_engine

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await bootstrap()
        yield
    finally:
        engine = get_engine()
        await engine.dispose()
