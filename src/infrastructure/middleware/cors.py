from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.config.settings import get_settings


def setup_cors(app: FastAPI) -> None:
    settings = get_settings()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
        allow_headers=['Authorization', 'Content-Type', 'X-CSRF-Token'],
    )
