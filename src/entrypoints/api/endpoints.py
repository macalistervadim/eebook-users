import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi_jwt import JwtAccessBearer, JwtAuthorizationCredentials
from pydantic import EmailStr
from starlette.responses import JSONResponse, Response

from src.config.settings import Settings
from src.schemas.api.auth import LoginSchema, UserWithTokens
from src.schemas.api.users import ChangePasswordSchema, UserCreateSchema, UserResponseSchema
from src.service_layer.auth_service import JWTAuthService
from src.service_layer.dependencies import get_auth_service, get_settings, get_user_service
from src.service_layer.users_service import UserService

router = APIRouter(prefix='/api/v1/users', tags=['users'])

logger = logging.getLogger(__name__)


settings_dependency = Depends(get_settings)


@router.get('/health')
async def health(settings: Settings = settings_dependency) -> JSONResponse:
    content = {
        'status': 'ok',
        'database': 'connected' if settings.POSTGRES_HOST else 'disconnected',
    }
    return JSONResponse(content=content, status_code=status.HTTP_200_OK)


@router.post('/register', response_model=UserWithTokens, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreateSchema,
    service: UserService = Depends(get_user_service),
    auth_service: JWTAuthService = Depends(get_auth_service),
) -> UserWithTokens:
    """Создаёт нового пользователя и сразу выдаёт токены."""
    user = await service.register_user(
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        email=user_data.email,
        username=user_data.username,
        password=user_data.password,
    )

    token_pair = auth_service.create_token_pair(user.id)

    return UserWithTokens(
        user=UserResponseSchema(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            username=user.username,
            is_active=user.is_active,
            is_verified=user.is_verified,
        ),
        tokens=token_pair,
    )


access_security = JwtAccessBearer(secret_key='dsafsdfs')


@router.post('/login', status_code=status.HTTP_200_OK)
async def login(
    login_data: LoginSchema,
    response: Response,
    service: UserService = Depends(get_user_service),
):
    token_pair = await service.login(
        email=login_data.email,
        password=login_data.password,
    )

    # Только refresh токен в HttpOnly куку
    access_security.set_refresh_cookie(response, token_pair.refresh_token)

    # Access токен возвращаем фронту в теле ответа
    return {
        'access_token': token_pair.access_token,
        'access_expires_at': token_pair.access_expires_at,
    }


@router.put('/change-password', status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    data: ChangePasswordSchema,
    credentials: JwtAuthorizationCredentials = Security(access_security),
    service: UserService = Depends(get_user_service),
) -> None:
    """Меняет пароль текущего пользователя.

    Args:
        data: Новые данные пароля.
        credentials: JWT-токен текущего пользователя.
        service: Сервис пользователей.

    Raises:
        HTTPException: Если пользователь не найден.

    """
    user_id = UUID(credentials['sub']['sub'])
    try:
        await service.change_password(user_id=user_id, new_password=data.new_password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found') from e


@router.put('/{user_id}/activate', status_code=status.HTTP_204_NO_CONTENT)
async def activate_user(user_id: UUID, service: UserService = Depends(get_user_service)) -> None:
    """Активирует пользователя."""
    await service.activate_user(user_id)
    return None


@router.put('/{user_id}/deactivate', status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_user(user_id: UUID, service: UserService = Depends(get_user_service)) -> None:
    """Деактивирует пользователя."""
    await service.deactivate_user(user_id)
    return None


@router.put('/{user_id}/verify-email', status_code=status.HTTP_204_NO_CONTENT)
async def verify_email(user_id: UUID, service: UserService = Depends(get_user_service)) -> None:
    """Подтверждает email пользователя."""
    await service.verify_email(user_id)
    return None


@router.get('/', response_model=list[UserResponseSchema])
async def list_users(
    only_active: bool = False,
    service: UserService = Depends(get_user_service),
) -> list[UserResponseSchema]:
    """Возвращает список пользователей."""
    users = await service.list_users(only_active=only_active)
    return [
        UserResponseSchema(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            username=user.username,
            is_active=user.is_active,
            is_verified=user.is_verified,
        )
        for user in users
    ]


@router.get('/{user_id}', response_model=UserResponseSchema)
async def get_user_by_id(
    user_id: UUID,
    service: UserService = Depends(get_user_service),
) -> UserResponseSchema:
    """Возвращает пользователя по ID."""
    user = await service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    return UserResponseSchema(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        username=user.username,
        is_active=user.is_active,
        is_verified=user.is_verified,
    )


@router.get('/by-email/', response_model=UserResponseSchema)
async def get_user_by_email(
    email: EmailStr,
    service: UserService = Depends(get_user_service),
) -> UserResponseSchema:
    """Возвращает пользователя по email."""
    user = await service.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    return UserResponseSchema(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        username=user.username,
        is_active=user.is_active,
        is_verified=user.is_verified,
    )


@router.get('/by-username/', response_model=UserResponseSchema)
async def get_user_by_username(
    username: str,
    service: UserService = Depends(get_user_service),
) -> UserResponseSchema:
    """Возвращает пользователя по username."""
    user = await service.get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    return UserResponseSchema(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        username=user.username,
        is_active=user.is_active,
        is_verified=user.is_verified,
    )
