"""Module that handles application level settings."""

from app.loaders import EnvironmentLoader
from app.utils.pydantic import ImmutableModel


class AppConfig(ImmutableModel):
    """Configuration model for application settings."""

    APP_NAME: str = "shibumi-store"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    APP_WORKERS: int = 1
    APP_DEBUG: bool = False
    APP_OPENAPI_URL: str | None = None
    APP_API_V1_PREFIX: str = "/api/v1"

    AUTH_SECRET_KEY: str
    AUTH_REFRESH_SECRET_KEY: str
    AUTH_ALGORITHM: str = "HS256"
    AUTH_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    AUTH_REFRESH_TOKEN_EXPIRE_MINUTES: int = 24 * 60  # 24 hours

    MONGODB_HOST: str
    MONGODB_PORT: int
    MONGODB_USER: str
    MONGODB_PASSWORD: str
    MONGODB_NAME: str
    MONGO_AUTH_SOURCE: str

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str

    SEND_GRID_API_KEY: str
    SEND_GRID_SENDER_EMAIL: str


SETTINGS = AppConfig.model_validate(EnvironmentLoader().load())
