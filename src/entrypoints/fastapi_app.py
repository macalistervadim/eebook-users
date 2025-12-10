from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi import status

from src.domain.exceptions.exceptions import DomainError
from src.entrypoints.api import endpoints
from src.entrypoints.api.exceptions import ApiError
from src.infrastructure.lifespan import lifespan
from src.infrastructure.middleware.cors import setup_cors


def create_app(*args, **kwargs) -> FastAPI:
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

    @app.exception_handler(DomainError)
    async def domain_error_handler(request: Request, exc: DomainError):
        return JSONResponse(
            status_code=400,
            content=ApiError(
                code=exc.code,
                message=exc.message,
                details=exc.details
            ).model_dump()
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception):
        # логируем exc полностью в Sentry/Logger
        return JSONResponse(
            status_code=500,
            content=ApiError(
                code="INTERNAL_SERVER_ERROR",
                message="Internal server error"
            ).model_dump()
        )


    setup_cors(app)

    return app
