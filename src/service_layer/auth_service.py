import logging
import uuid
from datetime import UTC, datetime

from asyncpg.pgproto.pgproto import timedelta

from src.adapters.auth.jwt_backend import JwtTokenAdapter
from src.adapters.interfaces import ABCAuthService, AbstractTimeProvider, AbstractTokenStore
from src.schemas.api.auth import TokenPair
from src.schemas.internal.auth import RefreshToken, TokenPayload, TokenType
from src.service_layer.uow import AbstractUnitOfWork

logger = logging.getLogger(__name__)


class JWTAuthService(ABCAuthService):
    """Сервис аутентификации, реализующий полную JWT-логику.

    Возможности:
    - генерация пары токенов (access + refresh);
    - валидация access-токена;
    - обмен refresh-токена на новую пару;
    - отзыв (revoke) токенов через TokenStore;
    - проверка на revoked перед аутентификацией.

    Args:
        jwt_backend: Бэкенд для генерации и декодирования JWT.
        token_store: Хранилище отозванных токенов.

    """

    def __init__(
        self,
        jwt_backend: JwtTokenAdapter,
        token_store: AbstractTokenStore,
        time_provider: AbstractTimeProvider,
    ):
        self._jwt = jwt_backend
        self._store = token_store
        self._time_provider = time_provider

    async def create_token_pair(
        self,
        uow: AbstractUnitOfWork,
        user_id: uuid.UUID,
        fingerprint: str,
    ) -> TokenPair:
        access, refresh = self._jwt.create_tokens(user_id)

        # Извлекаем JTI из refresh-токена
        refresh_payload = self._jwt.decode_token(refresh, 'refresh')
        jti = refresh_payload['jti']

        # Создаём refresh-токен в БД
        now = self._time_provider.now()
        refresh_token = RefreshToken(
            id=uuid.uuid4(),
            user_id=user_id,
            jti=jti,
            fingerprint=fingerprint,
            created_at=now,
            expires_at=now + self._jwt.refresh_expires_delta,
        )
        await uow.refresh_tokens.add(refresh_token)

        return TokenPair(
            access_token=access,
            refresh_token=str(refresh_token.id),
            access_expires_at=self._jwt.get_expires_at(self._jwt.decode_token(access, 'access')),
            refresh_expires_at=refresh_token.expires_at,
        )

    async def validate_access_token(self, token: str) -> TokenPayload | None:
        """Проверить access-токен.

        Логика:
        1. Декодировать токен.
        2. Проверить, что он не в blacklist.
        3. Вернуть нормализованный payload.

        Args:
            token: Строка access-токена.

        Returns:
            TokenPayload при успешной валидации или None.

        """
        payload = self._jwt.decode_token(token, 'access')
        if not payload:
            return None

        jti = payload['jti']
        if await self._store.is_revoked(jti):
            return None

        return TokenPayload(
            subject=uuid.UUID(payload['sub']),
            jti=uuid.UUID(jti),
            issued_at=datetime.fromtimestamp(payload['iat'], tz=UTC),
            expires_at=self._jwt.get_expires_at(payload),
            token_type=TokenType.ACCESS,
        )

    async def refresh_token_pair(self, refresh_token: str) -> TokenPair | None:
        """Обновить пару токенов по refresh-токену.

        Логика:
        1. Декодировать refresh.
        2. Проверить, что он не в blacklist.
        3. Сразу пометить refresh как revoked.
        4. Выдать новую пару токенов.

        Args:
            refresh_token: JWT refresh-токен.

        Returns:
            Новая TokenPair или None, если refresh недействителен.

        """
        payload = self._jwt.decode_token(refresh_token, 'refresh')
        if not payload:
            return None

        jti = payload['jti']
        if await self._store.is_revoked(jti):
            return None

        # Отзываем refresh, чтобы сделать его одноразовым
        await self._store.revoke(jti, self._jwt.refresh_expires_delta)

        user_id = uuid.UUID(payload['sub'])
        return await self.create_token_pair(user_id)

    async def revoke_token_pair(self, access_token: str, refresh_token: str) -> bool:
        """Отозвать оба токена пары — access и refresh.

        Используется при логауте.

        Args:
            access_token: Access-токен.
            refresh_token: Refresh-токен.

        Returns:
            bool: True при успешном отзыве, False если токены невалидны.

        """
        access_payload = self._jwt.decode_token(access_token, 'access')
        refresh_payload = self._jwt.decode_token(refresh_token, 'refresh')

        if not access_payload or not refresh_payload:
            return False

        now = datetime.now(UTC)

        access_remain = self._jwt.get_expires_at(access_payload) - now
        refresh_remain = self._jwt.get_expires_at(refresh_payload) - now

        await self._store.revoke(access_payload['jti'], max(access_remain, timedelta(seconds=1)))
        await self._store.revoke(refresh_payload['jti'], max(refresh_remain, timedelta(seconds=1)))

        return True
