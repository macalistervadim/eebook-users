from datetime import timedelta

from redis.asyncio import Redis

from src.adapters.abc_classes import ABCTokenStore


class RedisJwtRevocationStore(ABCTokenStore):
    def __init__(self, redis: Redis):
        self._redis = redis

    async def revoke(self, jti: str, expire_in: timedelta) -> None:
        seconds = int(expire_in.total_seconds())
        await self._redis.setex(f'revoked:{jti}', seconds, '1')

    async def is_revoked(self, jti: str) -> bool:
        return await self._redis.exists(f'revoked:{jti}') == 1
