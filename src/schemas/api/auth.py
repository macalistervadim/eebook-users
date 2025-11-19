from datetime import datetime

from pydantic import BaseModel, EmailStr

from src.schemas.api.users import UserResponseSchema


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    access_expires_at: datetime
    refresh_expires_at: datetime

    model_config = {
        'json_schema_extra': {
            'example': {
                'access_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
                'refresh_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
                'access_expires_at': '2025-11-18T14:30:00+00:00',
                'refresh_expires_at': '2025-12-03T12:00:00+00:00',
            },
        },
    }


class LoginSchema(BaseModel):
    email: EmailStr
    password: str


class UserWithTokens(BaseModel):
    user: UserResponseSchema
    tokens: TokenPair
