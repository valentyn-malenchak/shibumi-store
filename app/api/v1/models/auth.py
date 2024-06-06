"""Module that contains auth domain models."""

from pydantic import BaseModel


class JWTAccessToken(BaseModel):
    """JWT access token model."""

    access_token: str
    token_type: str


class JWTTokens(JWTAccessToken):
    """JWT access and refresh tokens model."""

    refresh_token: str


class JWTUser(BaseModel):
    """User data encapsulated to JWT."""

    id: str
    scopes: list[str]


class JWTPayload(JWTUser):
    """JWT payload model."""

    exp: int
