from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Pydantic-модель конфигурации приложения."""

    FASTAPI_SECRET: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int
    POSTGRES_HOST: str

    class Config:
        env_file_encoding = 'utf-8'
        extra = 'allow'

    @property
    def postgres_uri(self) -> str:
        return (
            f'postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}'
            f'@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}'
        )
