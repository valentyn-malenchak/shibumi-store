"""Module that contains auth domain routers."""

from fastapi import APIRouter, Depends, Security, status

from app.api.v1.auth.auth import Authentication, RefreshTokenAuthorization
from app.api.v1.auth.jwt import JWT
from app.api.v1.constants import ScopesEnum
from app.api.v1.models.auth import (
    JWTAccessToken,
    JWTTokens,
    JWTUser,
)
from app.api.v1.models.user import CurrentUser
from app.api.v1.services.role import RoleService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/tokens/", response_model=JWTTokens, status_code=status.HTTP_201_CREATED)
async def create_tokens(
    current_user: CurrentUser = Depends(Authentication()),
) -> dict[str, str]:
    """API which creates Access and Refresh tokens for user.

    Args:
        current_user (CurrentUser): Current authenticated user
        with permitted scopes.

    Returns:
        dict[str, str]: Access and Refresh JWTs.

    """
    return JWT.encode_tokens(
        data=JWTUser(id=str(current_user.object.id), scopes=current_user.scopes)
    )


@router.post(
    "/access-token/",
    response_model=JWTAccessToken,
    status_code=status.HTTP_201_CREATED,
)
async def refresh_access_token(
    current_user: CurrentUser = Security(
        RefreshTokenAuthorization(),
        scopes=[ScopesEnum.AUTH_REFRESH_TOKEN.name],
    ),
    role_service: RoleService = Depends(),
) -> dict[str, str]:
    """API which refreshes Access token using Refresh token.

    Args:
        current_user (CurrentUser): Current authorized user with permitted scopes.
        role_service (RoleService): Role service.

    Returns:
        dict[str, str]: New access token.

    """
    return JWT.encode_tokens(
        data=JWTUser(
            id=str(current_user.object.id),
            scopes=await role_service.get_scopes_by_roles(
                roles=current_user.object.roles
            ),
        ),
        include_refresh=False,
    )
