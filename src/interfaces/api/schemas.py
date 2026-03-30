from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, EmailStr


class ApiError(BaseModel):
    code: str
    message: str
    details: Optional[Any] = None


class UserResponseSchema(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: str
    username: str
    is_verified: bool
    role: str | None
    created_at: datetime

    @classmethod
    def from_domain(cls, user) -> 'UserResponseSchema':
        return cls(
            id=str(user.id),
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            username=user.username,
            is_verified=user.is_verified,
            role=str(user.role) if user.role is not None else None,
            created_at=user.created_at,
        )


class UserSubscriptionSchema(BaseModel):
    id: str
    user_id: str
    plan: str
    started_at: datetime
    expires_at: datetime | None
    is_active: bool


class ProfileSchema(BaseModel):
    user: UserResponseSchema
    user_subscription: UserSubscriptionSchema | None = None


class UserCreateSchema(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    username: str
    password: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    access_expires_at: datetime
    refresh_expires_at: datetime


class LoginSchema(BaseModel):
    email: EmailStr
    password: str


class AccessTokenSchema(BaseModel):
    access_token: str
    access_expires_at: datetime


class UserWithTokensSchema(BaseModel):
    user: UserResponseSchema
    access_token: AccessTokenSchema
