from datetime import datetime, timedelta

import jwt
from fastapi import FastAPI, HTTPException

from src.domain.model import User
from src.entity import models
from src.service_layer.uow import DEFAULT_SESSION_FACTORY, SqlAlchemyUnitOfWork

SECRET_KEY = "supersecretkey"

app = FastAPI(title="eebook")


# Регистрация
@app.post("/register")
async def register(data: models.RegisterModel):
    async with SqlAlchemyUnitOfWork(DEFAULT_SESSION_FACTORY) as uow:
        existing = await uow.users.get_by_email(data.email)
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Email already registered",
            )

        user = User(
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            hashed_password="",
        )
        user.set_password(data.password)
        uow.users.add(user)
        uow.commit()
        return {"msg": "User created"}


# Логин
@app.post("/login")
async def login(data: models.LoginModel):
    async with SqlAlchemyUnitOfWork(DEFAULT_SESSION_FACTORY) as uow:
        user = await uow.users.get_by_email(data.email)
        if not user or not user.check_password(data.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = jwt.encode(
            {"sub": user.email, "exp": datetime.utcnow() + timedelta(hours=1)},
            SECRET_KEY,
            algorithm="HS256",
        )
        return {"access_token": token}
