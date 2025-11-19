from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware


def setup_cors(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins='sddfs',
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )
