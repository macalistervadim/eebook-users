import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import UUID
from starlette.responses import JSONResponse, Response

from src.config.settings import Settings, get_settings
from src.entrypoints.api.exceptions import ApiError
from src.schemas.api.auth import AccessTokenSchema, LoginSchema, UserWithTokensSchema
from src.schemas.api.users import (
    ProfileSchema,
    UserCreateSchema,
    UserResponseSchema,
    UserSubscriptionSchema,
)
from src.service_layer.auth_service import JWTAuthService
from src.service_layer.dependencies import get_auth_service, get_uow, get_user_service
from src.service_layer.uow import AbstractUnitOfWork
from src.service_layer.users_service import UserService
from src.service_layer.utils import get_fingerprint
from src.utils.get_current_user import get_current_user_id

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


@router.get(
    '/me',
    response_model=ProfileSchema,
)
async def get_me(
    user_id: UUID = Depends(get_current_user_id),
    uow: AbstractUnitOfWork = Depends(get_uow),
):
    async with uow:
        user_entity = await uow.users.get_by_id(user_id)
        subscription = await uow.user_subscriptions.get_by_user_id(user_id)

    return ProfileSchema(
        user=UserResponseSchema.from_domain(user_entity),
        user_subscription=(
            UserSubscriptionSchema.from_domain(subscription) if subscription else None
        ),
    )


@router.post(
    '/register',
    status_code=status.HTTP_201_CREATED,
    response_model=UserWithTokensSchema,
    responses={
        400: {'model': ApiError, 'description': 'Доменные ошибки'},
        500: {'model': ApiError, 'description': 'Непредвиденная ошибка'},
    },
)
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


@router.post(
    '/login',
    response_model=AccessTokenSchema,
    responses={
        400: {'model': ApiError, 'description': 'Доменные ошибки'},
        500: {'model': ApiError, 'description': 'Непредвиденная ошибка'},
    },
)
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
    return AccessTokenSchema(
        access_token=token_pair.access_token,
        access_expires_at=token_pair.access_expires_at,
    )


# @router.put('/change-password', status_code=status.HTTP_204_NO_CONTENT)
# async def change_password(
#     data: ChangePasswordSchema,
#     credentials: JwtAuthorizationCredentials = Security(access_security),
#     service: UserService = Depends(get_user_service),
# ) -> None:
#     """Меняет пароль текущего пользователя.
#
#     Args:
#         data: Новые данные пароля.
#         credentials: JWT-токен текущего пользователя.
#         service: Сервис пользователей.
#
#     Raises:
#         HTTPException: Если пользователь не найден.
#
#     """
#     user_id = UUID(credentials['sub']['sub'])
#     try:
#         await service.change_password(user_id=user_id, new_password=data.new_password)
#     except ValueError as e:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found') from e


@router.post('/logout')
async def logout(
    request: Request,
    response: Response,
    auth_service: JWTAuthService = Depends(get_auth_service),
    uow: AbstractUnitOfWork = Depends(get_uow),
):
    refresh_token_id = request.cookies.get('refresh_token_id')
    if not refresh_token_id:
        raise HTTPException(401, 'Missing refresh token')

    try:
        token_id = uuid.UUID(refresh_token_id)
    except ValueError as e:
        raise HTTPException(400, 'Invalid token ID') from e

    async with uow:
        success = await auth_service.revoke_by_id(uow, token_id)
        if not success:
            # Можно логгировать, но не ошибку — токен мог уже быть отозван
            pass

    response.delete_cookie('refresh_token_id')
    return {'ok': True}


@router.post('/refresh', response_model=AccessTokenSchema)
async def refresh(
    request: Request,
    response: Response,
    service: UserService = Depends(get_user_service),
    settings: Settings = settings_dependency,
):
    refresh_token_id = request.cookies.get('refresh_token_id')
    if not refresh_token_id:
        raise HTTPException(401, 'Missing refresh token')

    fingerprint = get_fingerprint(request)

    async with service.uow as uow:
        new_pair = await service.auth_service.refresh_tokens(
            uow=uow,
            refresh_token_id=refresh_token_id,
            current_fingerprint=fingerprint,
        )
        if not new_pair:
            raise HTTPException(401, 'Invalid or revoked refresh token')

        # Обновляем куку
        response.set_cookie(
            key='refresh_token_id',
            value=new_pair.refresh_token,
            httponly=True,
            secure=True if not settings.DEBUG else False,
            samesite='strict',
            max_age=7 * 86400,
        )
        return AccessTokenSchema(
            access_token=new_pair.access_token,
            access_expires_at=new_pair.access_expires_at,
        )
