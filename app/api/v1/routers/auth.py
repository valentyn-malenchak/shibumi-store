"""Module that contains auth domain routers."""

from typing import Annotated, Dict

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.v1.auth.auth import Authentication, Authorization
from app.api.v1.auth.jwt import JWT
from app.api.v1.models.auth import (
    AccessTokenModel,
    RefreshTokenRequestModel,
    TokensModel,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/tokens/", response_model=TokensModel, status_code=status.HTTP_201_CREATED
)
async def create_tokens(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    authentication: Authentication = Depends(),
) -> Dict[str, str]:
    """API which creates Access and Refresh tokens for user.

    Args:
        form_data (OAuth2PasswordRequestForm): Form which contains
        username and password.
        authentication (Authentication): Authentication handler.

    Returns:
        Dict[str, str]: Access and Refresh JWTs.

    """

    user = await authentication.authenticate(form_data.username, form_data.password)

    token_data = user.get_token_data()

    return JWT.create_tokens(data=token_data)


@router.post(
    "/access-token/",
    response_model=AccessTokenModel,
    status_code=status.HTTP_201_CREATED,
)
async def refresh_access_token(
    request_body: RefreshTokenRequestModel,
    authorization: Authorization = Depends(),
) -> Dict[str, str]:
    """API which refreshes Access token using Refresh token.

    Args:
        request_body (RefreshTokenRequestModel): User's Refresh token.
        authorization (Authorization): Authorization handler.

    Returns:
        Dict[str, str]: New access token.

    """

    user = await authorization.authorize(request_body.refresh_token)

    token_data = user.get_token_data()

    return JWT.create_tokens(data=token_data, include_refresh=False)
