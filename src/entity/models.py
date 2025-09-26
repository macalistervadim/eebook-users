from pydantic import BaseModel


class RegisterModel(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str


class LoginModel(BaseModel):
    email: str
    password: str
