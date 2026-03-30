import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from starlette.responses import JSONResponse, Response

from src.application.auth_service import JWTAuthService
from src.application.dependencies import (
    get_auth_service,
    get_subscriptions_client,
    get_uow,
    get_user_service,
)
from src.application.uow import AbstractUnitOfWork
from src.application.utils import get_fingerprint
from src.application.user_service import UserService
from src.config.settings import Settings, get_settings
from src.infrastructure.clients.subscriptions import SubscriptionsClient
from src.interfaces.api.schemas import (
    AccessTokenSchema,
    ApiError,
    LoginSchema,
    ProfileSchema,
    UserCreateSchema,
    UserResponseSchema,
    UserWithTokensSchema,
)
from src.utils.get_current_user import get_current_user_id

router = APIRouter(prefix='/api/v1/users', tags=['users'])
logger = logging.getLogger(__name__)
settings_dependency = Depends(get_settings)
REFRESH_COOKIE_NAME = 'refresh_token_id'


def _build_refresh_cookie_params(*, settings: Settings, auth_service: JWTAuthService) -> dict:
    return {
        'key': REFRESH_COOKIE_NAME,
        'httponly': True,
        'secure': not settings.DEBUG,
        'samesite': 'strict',
        'path': '/',
        'max_age': int(auth_service.refresh_expires_delta.total_seconds()),
    }


@router.get('/health')
async def health(settings: Settings = settings_dependency) -> JSONResponse:
    content = {
        'status': 'ok',
        'database': 'connected' if settings.POSTGRES_HOST else 'disconnected',
    }
    return JSONResponse(content=content, status_code=status.HTTP_200_OK)


@router.get('/me', response_model=ProfileSchema)
async def get_me(
    user_id: uuid.UUID = Depends(get_current_user_id),
    uow: AbstractUnitOfWork = Depends(get_uow),
    subscriptions_client: SubscriptionsClient = Depends(get_subscriptions_client),
):
    async with uow:
        user_entity = await uow.users.get_by_id(user_id)
    subscription = await subscriptions_client.get_by_user_id(user_id)

    return ProfileSchema(
        user=UserResponseSchema.from_domain(user_entity),
        user_subscription=subscription,
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
        **_build_refresh_cookie_params(settings=settings, auth_service=service.auth_service),
        value=token_pair.refresh_token,
    )

    return UserWithTokensSchema(
        user=UserResponseSchema(
            id=str(user.id),
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            username=user.username,
            is_verified=user.is_verified,
            role=str(user.role) if user.role is not None else None,
            created_at=user.created_at,
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
    token_pair = await service.login(
        login_data.email,
        login_data.password,
        get_fingerprint(request),
    )
    response.set_cookie(
        **_build_refresh_cookie_params(settings=settings, auth_service=service.auth_service),
        value=token_pair.refresh_token,
    )
    return AccessTokenSchema(
        access_token=token_pair.access_token,
        access_expires_at=token_pair.access_expires_at,
    )


@router.post('/logout')
async def logout(
    request: Request,
    response: Response,
    auth_service: JWTAuthService = Depends(get_auth_service),
    uow: AbstractUnitOfWork = Depends(get_uow),
    settings: Settings = settings_dependency,
):
    refresh_token_id = request.cookies.get(REFRESH_COOKIE_NAME)
    if not refresh_token_id:
        raise HTTPException(401, 'Missing refresh token')

    try:
        token_id = uuid.UUID(refresh_token_id)
    except ValueError as exc:
        raise HTTPException(400, 'Invalid token ID') from exc

    async with uow:
        await auth_service.revoke_by_id(uow, token_id)

    response.delete_cookie(
        key=REFRESH_COOKIE_NAME,
        path='/',
        secure=not settings.DEBUG,
        httponly=True,
        samesite='strict',
    )
    return {'ok': True}


@router.post('/refresh', response_model=AccessTokenSchema)
async def refresh(
    request: Request,
    response: Response,
    service: UserService = Depends(get_user_service),
    settings: Settings = settings_dependency,
):
    refresh_token_id = request.cookies.get(REFRESH_COOKIE_NAME)
    if not refresh_token_id:
        raise HTTPException(401, 'Missing refresh token')

    async with service.uow as uow:
        new_pair = await service.auth_service.refresh_tokens(
            uow=uow,
            refresh_token_id=refresh_token_id,
            current_fingerprint=get_fingerprint(request),
        )
        if not new_pair:
            raise HTTPException(401, 'Invalid or revoked refresh token')

        response.set_cookie(
            **_build_refresh_cookie_params(settings=settings, auth_service=service.auth_service),
            value=new_pair.refresh_token,
        )
        return AccessTokenSchema(
            access_token=new_pair.access_token,
            access_expires_at=new_pair.access_expires_at,
        )
