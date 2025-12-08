import logging
from datetime import timedelta

from redis.asyncio import Redis

from src.adapters.abc_classes import ABCTokenStore
from src.infrastructure.logging.helpers.auth_helper import auth_log
from src.utils.auth_events import AuthEvent

logger = logging.getLogger(__name__)


class RedisJwtRevocationStore(ABCTokenStore):
    def __init__(self, redis: Redis):
        self._redis = redis

    async def revoke(self, jti: str, expire_in: timedelta) -> None:
        seconds = int(expire_in.total_seconds())
        await self._redis.setex(f'revoked:{jti}', seconds, '1')

        auth_log(
            AuthEvent.REFRESH_REVOKE_SUCCESS,
            'Refresh-токен помещён в blacklist',
            jti=jti,
            expires_in=seconds,
        )

    async def is_revoked(self, jti: str) -> bool:
        exists = await self._redis.exists(f'revoked:{jti}') == 1

        auth_log(
            AuthEvent.REFRESH_REVOKED_ATTEMPT if exists else AuthEvent.REFRESH_MISSING,
            'Проверка статуса refresh-токена',
            jti=jti,
            revoked=exists,
        )

        return exists
