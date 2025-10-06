from fastapi import APIRouter, Depends, status
from starlette.responses import JSONResponse

from src.config.settings import Settings
from src.service_layer.dependencies import get_settings

router = APIRouter(tags=['users'])


@router.get('/health')
async def health(settings: Settings = Depends(get_settings)) -> JSONResponse:
    content = {
        'status': 'ok',
        'database': 'connected' if settings.POSTGRES_HOST else 'disconnected',
    }
    return JSONResponse(content=content, status_code=status.HTTP_200_OK)
