import uuid

from httpx import AsyncClient, HTTPError, HTTPStatusError

from src.interfaces.api.schemas import UserSubscriptionSchema


class SubscriptionsClient:
    """HTTP client for the subscriptions microservice."""

    def __init__(self, http_client: AsyncClient) -> None:
        self._http_client = http_client

    async def get_by_user_id(self, user_id: uuid.UUID) -> UserSubscriptionSchema | None:
        try:
            response = await self._http_client.get(f'/api/v1/subscriptions/users/{user_id}')
            response.raise_for_status()
        except HTTPStatusError as exc:
            if exc.response.status_code == 404:
                return None
            raise
        except HTTPError:
            raise

        payload = response.json()
        return UserSubscriptionSchema.model_validate(payload)
