"""Module that contains auth domain routers."""

from typing import Annotated, Dict

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.api.v1.entities.auth import Authentication, Authorization
from app.api.v1.schemas.auth import AccessTokenSchema, TokensSchema
from app.constants import JTW_TYPE
from app.utils.jwt import JWT

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/tokens/", response_model=TokensSchema)
async def create_tokens(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Dict[str, str]:
    """API which creates Access and Refresh tokens for user.

    Args:
        form_data: Form which contains username and password.

    Returns:
        Access and Refresh JWTs.

    """

    # TODO: looks like code duplicate, investigate if could be done as dependency
    user = await Authentication.authenticate(form_data.username, form_data.password)

    token_data = user.get_token_data()

    return {
        "access_token": JWT.create_access_token(token_data),
        "refresh_token": JWT.create_refresh_token(token_data),
        "token_type": JTW_TYPE,
    }


@router.post("/access-token/", response_model=AccessTokenSchema)
async def refresh_access_token(refresh_token: str) -> Dict[str, str]:
    """API which refreshes Access token using Refresh token.

    Args:
        refresh_token: User's Refresh token.

    Returns:
        Access token.

    """

    # TODO: looks like code duplicate, investigate if could be done as dependency
    user = await Authorization.authorize(refresh_token)

    token_data = user.get_token_data()

    return {
        "access_token": JWT.create_access_token(token_data),
        "token_type": JTW_TYPE,
    }
