import os

from pydantic_settings import BaseSettings

from src.adapters.interfaces import ISecretsProvider
from src.adapters.vault import VaultClient


class Settings(BaseSettings):
    FASTAPI_SECRET: str

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int

    class Config:
        env_prefix = ''
        env_file_encoding = 'utf-8'
        extra = 'allow'


class SettingsLoader:
    """
    Класс, отвечающий только за загрузку секретов в окружение.
    Не создает Settings напрямую, не мапит вручную переменные.
    """

    def __init__(self, secrets_provider: ISecretsProvider | None = None):
        self._sp = secrets_provider or VaultClient()

    def load(self) -> None:
        """
        Загружает секреты из Vault и кладёт их в окружение.
        """
        secret_paths = [
            'eebook/users',
        ]

        for path in secret_paths:
            data = self._sp.read_secret(path)
            for key, value in data.items():
                os.environ[key] = str(value)


def get_postgres_uri() -> str:
    """
    Формирует строку подключения к PostgresDB asyncpg

    :return: str - строка подключения к postgres (asyncpg)
    """
    db_name = os.environ.get('POSTGRES_DB')
    db_user = os.environ.get('POSTGRES_USER')
    db_pass = os.environ.get('POSTGRES_PASSWORD')
    db_port = os.environ.get('POSTGRES_PORT')
    return f'postgresql+asyncpg://{db_user}:{db_pass}@postgres:{db_port}/{db_name}'
