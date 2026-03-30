import logging
import uuid

from httpx import AsyncClient, HTTPError, HTTPStatusError
from pydantic import ValidationError

from src.interfaces.api.schemas import UserSubscriptionSchema

logger = logging.getLogger(__name__)


class SubscriptionsClient:
    """HTTP client for the subscriptions microservice."""

    def __init__(self, http_client: AsyncClient | None) -> None:
        self._http_client = http_client

    async def get_by_user_id(self, user_id: uuid.UUID) -> UserSubscriptionSchema | None:
        if self._http_client is None:
            return None

        try:
            response = await self._http_client.get(f'/api/v1/subscriptions/users/{user_id}')
            response.raise_for_status()
        except HTTPStatusError as exc:
            if exc.response.status_code == 404:
                return None
            logger.warning(
                'Subscriptions service returned unexpected status',
                extra={'user_id': str(user_id), 'status_code': exc.response.status_code},
            )
            return None
        except HTTPError as exc:
            logger.warning(
                'Subscriptions service is unavailable',
                extra={'user_id': str(user_id), 'error': str(exc)},
            )
            return None

        try:
            payload = response.json()
            return UserSubscriptionSchema.model_validate(payload)
        except (ValueError, ValidationError) as exc:
            logger.warning(
                'Subscriptions service returned invalid payload',
                extra={'user_id': str(user_id), 'error': str(exc)},
            )
            return None
