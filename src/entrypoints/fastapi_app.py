from fastapi import FastAPI

from src.entrypoints.api import endpoints
from src.infrastructure.lifespan import lifespan


def create_app() -> FastAPI:
    app = FastAPI(
        title='eebook',
        description='API учета инвестиций eebook',
        version='0.1.0',
        docs_url='/api/docs',
        redoc_url='/api/redoc',
        openapi_url='/api/openapi.json',
        lifespan=lifespan,
    )

    app.include_router(endpoints.router)

    return app


app = create_app()
