from fastapi import APIRouter, Depends

from src.config.settings import Settings
from src.service_layer.dependencies import get_settings

router = APIRouter(prefix='/eebook-users', tags=['users'])


@router.get('/health')
async def health(settings: Settings = Depends(get_settings)):
    return {
        'status': 'ok',
        'database': 'connected' if settings.POSTGRES_HOST else 'disconnected',
    }
