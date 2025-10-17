from uuid import UUID

from pydantic import BaseModel, EmailStr


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
    username: str
    is_active: bool
    is_verified: bool


class ChangePasswordSchema(BaseModel):
    new_password: str
