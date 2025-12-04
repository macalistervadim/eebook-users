import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt as pyjwt
from fastapi_jwt import JwtAccessBearer

from src.adapters.abc_classes import ABCTimeProvider


class JwtTokenAdapter:
    """Адаптер для работы с JWT-токенами.

    Реализует паттерн «Адаптер» (GoF): инкапсулирует
    fastapi_jwt и предоставляет стабильный интерфейс
    для application layer.

    - генерацию JTI (уникальный идентификатор токена);
    - независимое создание access и refresh токена;
    - явную ручную валидацию и декодирование токена;
    - строгую проверку корректности типа токена (access/refresh);
    - извлечение времени истечения токена.

    Args:
        secret_key: Секретный ключ для подписи JWT.
        algorithm: Алгоритм подписи (по умолчанию HS256).
        access_expires_delta: Срок жизни access-токена.
        refresh_expires_delta: Срок жизни refresh-токена.
        time_provider: Поставщик времени

    """

    def __init__(
        self,
        secret_key: str,
        time_provider: ABCTimeProvider,
        algorithm: str = 'HS256',
        access_expires_delta: timedelta = timedelta(minutes=15),
        refresh_expires_delta: timedelta = timedelta(days=15),
    ):
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._access_expires_delta = access_expires_delta
        self._refresh_expires_delta = refresh_expires_delta
        self._time_provider = time_provider
        self._fastapi_jwt = JwtAccessBearer(
            secret_key=secret_key,
            algorithm=algorithm,
            access_expires_delta=access_expires_delta,
            refresh_expires_delta=refresh_expires_delta,
            auto_error=False,
        )

    def create_tokens(self, subject: uuid.UUID) -> tuple[str, str]:
        """Создать пару access/refresh токенов.

        Args:
            subject: Идентификатор субъекта (обычно user_id).

        Returns:
            Пара токенов (access_token, refresh_token).

        Raises:
            RuntimeError: Если не удалось сгенерировать токены.

        """
        now = self._time_provider.now()

        access_jti = uuid.uuid4()
        refresh_jti = uuid.uuid4()

        access_payload = {
            'sub': str(subject),
            'jti': str(access_jti),
            'iat': int(now.timestamp()),
        }

        refresh_payload = {
            'sub': str(subject),
            'jti': str(refresh_jti),
            'iat': int(now.timestamp()),
            'refresh': True,
        }

        access_token = self._fastapi_jwt.create_access_token(subject=access_payload)
        refresh_token = self._fastapi_jwt.create_refresh_token(subject=refresh_payload)

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
                self._secret_key,
                algorithms=[self._algorithm],
                options={'require': ['exp', 'iat', 'jti']},
            )

            subject = payload.get('subject')
            if not subject:
                return None

            token_type = payload.get('type')
            if token_type not in ('access', 'refresh'):
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
