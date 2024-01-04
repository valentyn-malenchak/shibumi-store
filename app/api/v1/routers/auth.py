"""Module that contains auth domain routers."""

from typing import Annotated, Dict

from fastapi import APIRouter, Depends, Security, status

from app.api.v1.auth.auth import Authentication, StrictAuthorization
from app.api.v1.auth.jwt import JWT
from app.api.v1.constants import ScopesEnum
from app.api.v1.models.auth import (
    AccessTokenModel,
    TokensModel,
    TokenUserModel,
)
from app.api.v1.models.users import User
from app.api.v1.services.roles_scopes import RoleScopeService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/tokens/", response_model=TokensModel, status_code=status.HTTP_201_CREATED
)
async def create_tokens(
    user: Annotated[User, Depends(Authentication())],
    role_scope_service: RoleScopeService = Depends(),
) -> Dict[str, str]:
    """API which creates Access and Refresh tokens for user.

    Args:
        user (User): Authenticated user.
        role_scope_service (RoleScopeService): Roles-scopes service.

    Returns:
        Dict[str, str]: Access and Refresh JWTs.

    """

    return JWT.encode_tokens(
        data=TokenUserModel(
            id=user.id,
            scopes=await role_scope_service.get_scopes_by_roles(roles=user.roles),
        )
    )


@router.post(
    "/access-token/",
    response_model=AccessTokenModel,
    status_code=status.HTTP_201_CREATED,
)
async def refresh_access_token(
    user: User = Security(
        StrictAuthorization(is_refresh_token=True),
        scopes=[ScopesEnum.AUTH_REFRESH_TOKEN.name],
    ),
    role_scope_service: RoleScopeService = Depends(),
) -> Dict[str, str]:
    """API which refreshes Access token using Refresh token.

    Args:
        user (User): Current User object.
        role_scope_service (RoleScopeService): Roles-scopes service.

    Returns:
        Dict[str, str]: New access token.

    """

    return JWT.encode_tokens(
        data=TokenUserModel(
            id=user.id,
            scopes=await role_scope_service.get_scopes_by_roles(roles=user.roles),
        ),
        include_refresh=False,
    )
