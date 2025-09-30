from fastapi import FastAPI
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)

from src.bootstrap import async_bootstrap, bootstrap
from src.config import get_postgres_uri

settings = bootstrap()

# Создаём session factory здесь, после инициализации
DEFAULT_SESSION_FACTORY = async_sessionmaker(
    bind=create_async_engine(
        get_postgres_uri(),
        isolation_level='REPEATABLE READ',
    ),
    expire_on_commit=False,
)

app = FastAPI(title='eebook')


@app.on_event('startup')
async def on_startup():
    await async_bootstrap(settings)


# Регистрация
# @app.post('/register')
# async def register(data: models.RegisterModel):
#     async with SqlAlchemyUnitOfWork(DEFAULT_SESSION_FACTORY) as uow:
#         existing = await uow.users.get_by_email(data.email)
#         if existing:
#             raise HTTPException(
#                 status_code=400,
#                 detail='Email already registered',
#             )
#
#         user = User(
#             first_name=data.first_name,
#             last_name=data.last_name,
#             email=data.email,
#             hashed_password='',
#         )
#         user.set_password(data.password)
#         uow.users.add(user)
#         await uow.commit()
#         return {'msg': 'User created'}
#
#
# # Логин
# @app.post('/login')
# async def login(data: models.LoginModel):
#     async with SqlAlchemyUnitOfWork(DEFAULT_SESSION_FACTORY) as uow:
#         user = await uow.users.get_by_email(data.email)
#         if not user or not user.check_password(data.password):
#             raise HTTPException(status_code=401, detail='Invalid credentials')
#
#         token = jwt.encode(
#             {'sub': user.email, 'exp': datetime.utcnow() + timedelta(hours=1)},
#             settings.FASTAPI_SECRET,
#             algorithm='HS256',
#         )
#         return {'access_token': token}
