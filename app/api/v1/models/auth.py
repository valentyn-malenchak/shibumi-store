"""Module that contains auth domain models."""


from pydantic import BaseModel


class AccessTokenModel(BaseModel):
    """JWT access token model."""

    access_token: str
    token_type: str


class TokensModel(AccessTokenModel):
    """JWT access and refresh tokens model."""

    refresh_token: str


class TokenUserModel(BaseModel):
    """User data encapsulated to JWT."""

    id: str
    scopes: list[str]


class TokenPayloadModel(TokenUserModel):
    """JWT payload model."""

    exp: int
