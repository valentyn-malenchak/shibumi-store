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
from app.api.v1.models.users import CurrentUserModel
from app.api.v1.services.roles_scopes import RoleScopeService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/tokens/", response_model=TokensModel, status_code=status.HTTP_201_CREATED
)
async def create_tokens(
    current_user: Annotated[CurrentUserModel, Depends(Authentication())],
) -> Dict[str, str]:
    """API which creates Access and Refresh tokens for user.

    Args:
        current_user (CurrentUserModel): Authenticated user with permitted scopes.

    Returns:
        Dict[str, str]: Access and Refresh JWTs.

    """

    return JWT.encode_tokens(
        data=TokenUserModel(id=current_user.object.id, scopes=current_user.scopes)
    )


@router.post(
    "/access-token/",
    response_model=AccessTokenModel,
    status_code=status.HTTP_201_CREATED,
)
async def refresh_access_token(
    current_user: CurrentUserModel = Security(
        StrictAuthorization(is_refresh_token=True),
        scopes=[ScopesEnum.AUTH_REFRESH_TOKEN.name],
    ),
    role_scope_service: RoleScopeService = Depends(),
) -> Dict[str, str]:
    """API which refreshes Access token using Refresh token.

    Args:
        current_user (CurrentUserModel): Authorized user with permitted scopes.
        role_scope_service (RoleScopeService): Roles-scopes service.

    Returns:
        Dict[str, str]: New access token.

    """

    return JWT.encode_tokens(
        data=TokenUserModel(
            id=current_user.object.id,
            scopes=await role_scope_service.get_scopes_by_roles(
                roles=current_user.object.roles
            ),
        ),
        include_refresh=False,
    )
