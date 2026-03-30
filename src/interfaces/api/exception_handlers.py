import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from src.domain.exceptions.exceptions import DomainError
from src.interfaces.api.schemas import ApiError

logger = logging.getLogger(__name__)


def _request_id(request: Request) -> str:
    return getattr(request.state, 'request_id', '-')


def setup_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
        logger.warning(
            'request.domain_error code=%s method=%s path=%s request_id=%s',
            exc.code,
            request.method,
            request.url.path,
            _request_id(request),
        )
        return JSONResponse(
            status_code=400,
            content=ApiError(code=exc.code, message=exc.message, details=exc.details).model_dump(),
        )

    @app.exception_handler(HTTPException)
    async def http_error_handler(request: Request, exc: HTTPException) -> JSONResponse:
        logger.warning(
            'request.http_error status=%s method=%s path=%s request_id=%s',
            exc.status_code,
            request.method,
            request.url.path,
            _request_id(request),
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={'detail': exc.detail, 'request_id': _request_id(request)},
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception(
            'request.unhandled_error method=%s path=%s request_id=%s',
            request.method,
            request.url.path,
            _request_id(request),
        )
        return JSONResponse(
            status_code=500,
            content={'detail': 'Internal server error', 'request_id': _request_id(request)},
        )
