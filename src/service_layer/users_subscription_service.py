import uuid

from src.adapters.abc_classes import ABCTimeProvider
from src.adapters.interfaces import IPasswordHasher
from src.domain.exceptions.exceptions import InvalidCredentialsError
from src.domain.model import UserSubscription
from src.schemas.internal.subscription import SubscriptionPlan
from src.service_layer.uow import AbstractUnitOfWork


class UsersSubscriptionService:
    """Сервисный слой для работы с подписками пользователей."""

    def __init__(
        self,
        uow: AbstractUnitOfWork,
        hasher: IPasswordHasher,
        time_provider: ABCTimeProvider,
    ):
        self._uow = uow
        self._hasher = hasher
        self._time_provider = time_provider

    async def add_subscription(self, user_id: uuid.UUID, plan: SubscriptionPlan):
        async with self._uow as uow:
            user = await uow.users.get_by_id(user_id)
            if not user:
                raise InvalidCredentialsError()

            user_subscription = UserSubscription(
                user_id=user_id,
                plan=plan,
                started_at=self._time_provider.now(),
                expires_at=None,
                is_active=True,
            )
            await uow.user_subscriptions.add(user_subscription)
            await uow.commit()
            return user_subscription

    async def get_by_id(self, user_sub_id: uuid.UUID) -> UserSubscription | None:
        async with self._uow as uow:
            return await uow.user_subscriptions.get_by_id(user_sub_id)

    async def get_by_user_id(self, user_id: uuid.UUID) -> UserSubscription | None:
        async with self._uow as uow:
            return await uow.user_subscriptions.get_by_user_id(user_id)
