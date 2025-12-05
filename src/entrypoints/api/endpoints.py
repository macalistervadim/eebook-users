import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Security, status
from fastapi_jwt import JwtAccessBearer, JwtAuthorizationCredentials
from starlette.responses import JSONResponse, Response

from src.config.settings import Settings, get_settings
from src.schemas.api.auth import AccessTokenSchema, LoginSchema, UserWithTokensSchema
from src.schemas.api.users import ChangePasswordSchema, UserCreateSchema, UserResponseSchema
from src.service_layer.dependencies import get_user_service
from src.service_layer.users_service import UserService
from src.service_layer.utils import get_fingerprint

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


@router.post('/register', status_code=status.HTTP_201_CREATED, response_model=UserWithTokensSchema)
async def register(
    register_data: UserCreateSchema,
    request: Request,
    response: Response,
    service: UserService = Depends(get_user_service),
    settings: Settings = settings_dependency,
) -> UserWithTokensSchema:
    fingerprint = get_fingerprint(request)

    user, token_pair = await service.register_user(
        first_name=register_data.first_name,
        last_name=register_data.last_name,
        email=register_data.email,
        username=register_data.username,
        password=register_data.password,
        fingerprint=fingerprint,
    )

    response.set_cookie(
        key='refresh_token_id',
        value=token_pair.refresh_token,
        httponly=True,
        secure=True if not settings.DEBUG else False,
        samesite='lax',
        max_age=7 * 24 * 60 * 60,
    )

    return UserWithTokensSchema(
        user=UserResponseSchema(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            username=user.username,
            is_active=user.is_active,
            is_verified=user.is_verified,
        ),
        access_token=AccessTokenSchema(
            access_token=token_pair.access_token,
            access_expires_at=token_pair.access_expires_at,
        ),
    )


access_security = JwtAccessBearer(secret_key='dsafsdfs')


@router.post('/login', response_model=AccessTokenSchema)
async def login(
    login_data: LoginSchema,
    request: Request,
    response: Response,
    service: UserService = Depends(get_user_service),
    settings: Settings = settings_dependency,
) -> AccessTokenSchema:
    fingerprint = get_fingerprint(request)

    token_pair = await service.login(login_data.email, login_data.password, fingerprint)

    response.set_cookie(
        key='refresh_token_id',
        value=token_pair.refresh_token,
        httponly=True,
        secure=True if not settings.DEBUG else False,
        samesite='strict',
        max_age=7 * 24 * 60 * 60,
    )
    return AccessTokenSchema(token_pair.access_token, token_pair.access_expires_at)


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
