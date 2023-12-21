"""Module that handles application level settings."""


from app.loaders import EnvironmentLoader
from app.utils.pydantic import ImmutableModel


class AppConfig(ImmutableModel):
    """Configuration model for application settings."""

    APP_NAME: str = "fastapi-shop"
    APP_WORKERS: int = 1
    APP_DEBUG: bool = False

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


SETTINGS = AppConfig.model_validate(EnvironmentLoader().load())
