"""Module that handles application level settings."""

from pydantic import BaseModel

from app.loaders import EnvironmentLoader


class AppConfig(BaseModel):
    """Configuration model for application settings."""

    APP_NAME: str = "fastapi-shop"
    DEBUG: bool = False

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


SETTINGS = AppConfig.model_validate(EnvironmentLoader.load())
