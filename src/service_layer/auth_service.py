import logging
import uuid
from datetime import UTC, datetime

from src.adapters.abc_classes import ABCAuthService, ABCTimeProvider, ABCTokenStore
from src.adapters.auth.jwt_backend import JwtTokenAdapter
from src.infrastructure.logging.helpers.auth_helper import auth_log
from src.schemas.api.auth import TokenPair
from src.schemas.internal.auth import RefreshToken, TokenPayload, TokenType
from src.service_layer.uow import AbstractUnitOfWork
from src.utils.auth_events import AuthEvent

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
        time_provider: Сервис для работы со временем.

    """

    def __init__(
        self,
        jwt_backend: JwtTokenAdapter,
        token_store: ABCTokenStore,
        time_provider: ABCTimeProvider,
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
        # if not access or refresh:
        #     raise ValueError('tokens not generated')

        refresh_payload = self._jwt.decode_token(refresh, 'refresh')
        if refresh_payload:
            jti = refresh_payload['jti']

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
        auth_log(
            AuthEvent.REFRESH_ISSUED,
            'Выпущен новый refresh-token',
            user_id=user_id,
            refresh_id=refresh_token.id,
            jti=jti,
        )

        auth_log(
            AuthEvent.ACCESS_REFRESH_CREATED,
            'Сгенерирована новая пара access/refresh токенов',
            user_id=user_id,
        )

        access_payload = self._jwt.decode_token(access, 'access')
        if access_payload is None:
            raise ValueError('Access token decoding failed')

        return TokenPair(
            access_token=access,
            refresh_token=str(refresh_token.id),
            access_expires_at=self._jwt.get_expires_at(access_payload),
            refresh_expires_at=refresh_token.expires_at,
        )

    async def validate_access_token(self, token: str) -> TokenPayload | None:
        payload = self._jwt.decode_token(token, 'access')
        if not payload:
            return None

        expires_at = self._jwt.get_expires_at(payload)
        if expires_at is None:
            return None

        return TokenPayload(
            subject=uuid.UUID(payload['sub']),
            jti=uuid.UUID(payload['jti']),
            issued_at=datetime.fromtimestamp(payload['iat'], tz=UTC),
            expires_at=expires_at,
            token_type=TokenType.ACCESS,
        )

    async def revoke_by_id(
        self,
        uow: AbstractUnitOfWork,
        refresh_token_id: uuid.UUID,
    ) -> bool:
        token = await uow.refresh_tokens.get_by_id(refresh_token_id)

        if not token or token.is_revoked:
            auth_log(
                AuthEvent.REFRESH_MISSING,
                'Попытка отозвать несуществующий или уже отозванный refresh-token',
                refresh_id=refresh_token_id,
            )
            return False

        now = self._time_provider.now()

        token.revoke(now)
        await uow.refresh_tokens.update(token)

        await self._store.revoke(str(token.jti), token.expires_at - now)

        auth_log(
            AuthEvent.REFRESH_REVOKE_SUCCESS,
            'Refresh-token успешно отозван',
            refresh_id=refresh_token_id,
            user_id=token.user_id,
        )

        return True

    async def refresh_tokens(
        self,
        uow: AbstractUnitOfWork,
        refresh_token_id: str,
        current_fingerprint: str,
    ) -> TokenPair | None:
        try:
            token_id = uuid.UUID(refresh_token_id)
        except ValueError:
            return None

        token = await uow.refresh_tokens.get_by_id(token_id)
        if not token or token.is_revoked:
            auth_log(
                AuthEvent.REFRESH_REVOKED_ATTEMPT,
                'Попытка обновления пары через отозванный refresh-token',
                refresh_id=refresh_token_id,
            )
            return None

        now = self._time_provider.now()

        if now > token.expires_at:
            auth_log(
                AuthEvent.REFRESH_EXPIRED,
                'Попытка использования просроченного refresh-token',
                refresh_id=refresh_token_id,
            )
            return None

        if token.fingerprint != current_fingerprint:
            await uow.refresh_tokens.revoke_all_for_user(token.user_id, now)
            await uow.commit()

            auth_log(
                AuthEvent.REFRESH_FINGERPRINT_MISMATCH,
                'Несовпадение fingerprint — все токены пользователя отозваны',
                user_id=token.user_id,
                refresh_id=refresh_token_id,
            )
            return None

        token.revoke(now)
        await uow.refresh_tokens.update(token)

        auth_log(
            AuthEvent.REFRESH_ROTATE,
            'Refresh-токен отозван перед выдачей нового',
            user_id=token.user_id,
            refresh_id=refresh_token_id,
        )

        return await self.create_token_pair(
            uow=uow,
            user_id=token.user_id,
            fingerprint=current_fingerprint,
        )
