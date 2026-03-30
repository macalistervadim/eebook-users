"""HTTP middleware for request id and request logging."""

import logging
import time
from uuid import uuid4

from fastapi import FastAPI, Request

from src.infrastructure.logging.context import (
    reset_request_id,
    reset_user_id,
    set_request_id,
    set_user_id,
)

logger = logging.getLogger(__name__)


def setup_request_context(app: FastAPI) -> None:
    """Install request context middleware."""

    @app.middleware('http')
    async def request_context_middleware(request: Request, call_next):
        request_id = request.headers.get('X-Request-ID') or str(uuid4())
        request.state.request_id = request_id

        request_id_token = set_request_id(request_id)
        user_id_token = set_user_id('-')
        started_at = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception:
            duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
            logger.exception(
                'request.failed method=%s path=%s duration_ms=%s request_id=%s',
                request.method,
                request.url.path,
                duration_ms,
                request_id,
            )
            raise
        else:
            duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
            response.headers['X-Request-ID'] = request_id
            logger.info(
                'request.completed method=%s path=%s status_code=%s duration_ms=%s request_id=%s',
                request.method,
                request.url.path,
                response.status_code,
                duration_ms,
                request_id,
            )
            return response
        finally:
            reset_user_id(user_id_token)
            reset_request_id(request_id_token)
