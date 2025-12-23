from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr

from src.domain.model import User, UserSubscription
from src.schemas.internal.role import UserRole
from src.schemas.internal.subscription import SubscriptionPlan


class UserCreateSchema(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    username: str
    password: str


class UserResponseSchema(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: EmailStr
    role: UserRole
    created_at: datetime
    username: str
    is_active: bool
    is_verified: bool

    @classmethod
    def from_domain(cls, user: User):
        return cls(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            role=user.role,
            username=user.username,
            created_at=user.created_at,
            is_active=user.is_active,
            is_verified=user.is_verified,
        )


class ChangePasswordSchema(BaseModel):
    new_password: str


class UserSubscriptionSchema(BaseModel):
    id: UUID
    user_id: UUID
    plan: SubscriptionPlan
    started_at: datetime
    expires_at: datetime | None
    is_active: bool

    @classmethod
    def from_domain(cls, subscription: UserSubscription):
        return cls(
            id=subscription.id,
            user_id=subscription.user_id,
            plan=subscription.plan,
            started_at=subscription.started_at,
            expires_at=subscription.expires_at,
            is_active=subscription.is_active,
        )


class ProfileSchema(BaseModel):
    user: UserResponseSchema
    user_subscription: UserSubscriptionSchema | None
