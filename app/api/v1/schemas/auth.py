"""Module that contains auth domain schemas."""

from pydantic import BaseModel


class AccessTokenSchema(BaseModel):
    """JWT access token schema."""

    access_token: str
    token_type: str


class TokensSchema(AccessTokenSchema):
    """JWT access and refresh tokens schema."""

    refresh_token: str


class TokenUserData(BaseModel):
    """User data encapsulated to JWT"""

    first_name: str
    last_name: str
    username: str


class TokenPayload(TokenUserData):
    """JWT payload schema."""

    exp: int
