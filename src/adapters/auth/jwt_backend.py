import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt as pyjwt

from src.adapters.abc_classes import ABCTimeProvider


class JwtTokenAdapter:
    """Адаптер для работы с JWT-токенами.

    Реализует паттерн «Адаптер» (GoF) и предоставляет
    стабильный интерфейс для application layer.

    - генерацию JTI (уникальный идентификатор токена);
    - независимое создание access и refresh токена;
    - явную ручную валидацию и декодирование токена;
    - строгую проверку корректности типа токена (access/refresh);
    - извлечение времени истечения токена.

    Args:
        signing_key: Ключ для подписи JWT (секрет для HS256, private key для RS256).
        verification_key: Ключ для проверки подписи (по умолчанию signing_key).
        algorithm: Алгоритм подписи.
        access_expires_delta: Срок жизни access-токена.
        refresh_expires_delta: Срок жизни refresh-токена.
        time_provider: Поставщик времени

    """

    def __init__(
        self,
        signing_key: str,
        time_provider: ABCTimeProvider,
        verification_key: str | None = None,
        algorithm: str = 'HS256',
        access_expires_delta: timedelta = timedelta(minutes=15),
        refresh_expires_delta: timedelta = timedelta(days=15),
    ):
        self._signing_key = signing_key
        self._verification_key = verification_key or signing_key
        self._algorithm = algorithm
        self._access_expires_delta = access_expires_delta
        self._refresh_expires_delta = refresh_expires_delta
        self._time_provider = time_provider

    def _build_payload(
        self,
        subject: uuid.UUID,
        token_version: int,
        token_type: str,
        ttl: timedelta,
    ) -> dict[str, Any]:
        now = self._time_provider.now()
        expires_at = now + ttl
        return {
            'sub': str(subject),
            'jti': str(uuid.uuid4()),
            'iat': int(now.timestamp()),
            'nbf': int(now.timestamp()),
            'exp': int(expires_at.timestamp()),
            'token_version': token_version,
            'type': token_type,
        }

    def create_tokens(self, subject: uuid.UUID, token_version: int) -> tuple[str, str]:
        """Создать пару access/refresh токенов.

        Args:
            subject: Идентификатор субъекта (обычно user_id).

        Returns:
            Пара токенов (access_token, refresh_token).

        Raises:
            RuntimeError: Если не удалось сгенерировать токены.

        """
        access_payload = self._build_payload(
            subject=subject,
            token_version=token_version,
            token_type='access',
            ttl=self._access_expires_delta,
        )
        refresh_payload = self._build_payload(
            subject=subject,
            token_version=token_version,
            token_type='refresh',
            ttl=self._refresh_expires_delta,
        )

        access_token = pyjwt.encode(
            payload=access_payload,
            key=self._signing_key,
            algorithm=self._algorithm,
        )
        refresh_token = pyjwt.encode(
            payload=refresh_payload,
            key=self._signing_key,
            algorithm=self._algorithm,
        )

        return access_token, refresh_token

    def decode_token(self, token: str, expected_type: str) -> dict[str, Any] | None:
        """Расшифровать и провалидировать JWT.

        Проверяет:
        - корректность подписи;
        - наличие обязательных полей (`exp`, `iat`, `jti`, `sub`);
        - корректность типа токена (refresh/access).

        Args:
            token: JWT-строка.
            expected_type: Ожидаемый тип токена (`"access"` или `"refresh"`).

        Returns:
            Расшифрованный payload или None, если токен недействителен.

        """
        try:
            payload = pyjwt.decode(
                token,
                self._verification_key,
                algorithms=[self._algorithm],
                options={'require': ['exp', 'iat', 'nbf', 'jti', 'sub', 'token_version', 'type']},
            )

            subject = payload.get('sub')
            if not subject:
                return None

            token_type = payload.get('type')
            if token_type not in ('access', 'refresh'):
                return None

            token_version = payload.get('token_version')
            if not isinstance(token_version, int) or token_version < 0:
                return None

            if token_type != expected_type:
                return None

            return payload

        except pyjwt.PyJWTError:
            return None

    def get_expires_at(self, payload: dict[str, Any]) -> datetime:
        """Получить время истечения токена.

        Args:
            payload: Payload токена.

        Returns:
            datetime: Абсолютное время истечения (UTC).

        """
        return datetime.fromtimestamp(payload['exp'], tz=UTC)

    @property
    def access_expires_delta(self) -> timedelta:
        """timedelta: Срок жизни access-токена."""
        return self._access_expires_delta

    @property
    def refresh_expires_delta(self) -> timedelta:
        """timedelta: Срок жизни refresh-токена."""
        return self._refresh_expires_delta
