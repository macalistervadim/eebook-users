from src.bootstrap import bootstrap
from src.entrypoints.fastapi_app import create_app


def create_app_sync():
    settings = bootstrap()
    return create_app(settings)
