"""Module that contains auth domain models."""

from pydantic import BaseModel


class AccessJWT(BaseModel):
    """Access JWT model."""

    access_token: str
    token_type: str


class JWTs(AccessJWT):
    """Access and refresh JWTs model."""

    refresh_token: str


class JWTUser(BaseModel):
    """User data encapsulated to JWT."""

    id: str
    scopes: list[str]


class JWTPayload(JWTUser):
    """JWT payload model."""

    exp: int
