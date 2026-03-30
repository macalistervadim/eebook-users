import logging
from uuid import UUID

from fastapi import Depends, Request
from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.application.auth_service import JWTAuthService
from src.application.dependencies import get_auth_service

logger = logging.getLogger(__name__)
access_security = HTTPBearer(auto_error=False)


async def get_current_user_id(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(access_security),
    auth_service: JWTAuthService = Depends(get_auth_service),
) -> UUID:
    if not credentials or credentials.scheme.lower() != 'bearer':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token')

    payload = await auth_service.validate_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token')

    request.state.user_id = str(payload.subject)
    return payload.subject
