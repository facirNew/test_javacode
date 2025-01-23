from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment variables load"""

    PG_DATABASE: str = None
    PG_USER: str = None
    PG_PASS: str = None
    PG_HOST: str = None
    PG_PORT: str = None
    REDIS_HOST: str = None
    REDIS_PORT: int = 6379

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')


settings = Settings()


def get_db_url() -> str:
    return (f'postgresql+asyncpg://{settings.PG_USER}:{settings.PG_PASS}@'
            f'{settings.PG_HOST}:{settings.PG_PORT}/{settings.PG_DATABASE}')


def get_redis_url() -> str:
    return f'redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}'
