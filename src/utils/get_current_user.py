import logging
from uuid import UUID

from fastapi import Security
from fastapi_jwt import JwtAccessBearer, JwtAuthorizationCredentials

from src.domain.exceptions.exceptions import InvalidCredentialsError

access_security = JwtAccessBearer(secret_key='123')
logger = logging.getLogger(__name__)


def get_current_user_id(
    credentials: JwtAuthorizationCredentials = Security(access_security),
) -> UUID:
    try:
        return UUID(credentials['sub'])
    except Exception:
        raise InvalidCredentialsError()
