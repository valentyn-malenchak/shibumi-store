"""Module that contains role domain routers."""

from typing import Any

from fastapi import APIRouter, Depends, Security, status

from app.api.v1.auth.auth import OptionalAuthorization
from app.api.v1.constants import ScopesEnum
from app.api.v1.models.role import RolesListModel
from app.api.v1.models.user import CurrentUserModel
from app.api.v1.services.role import RoleService

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("/", response_model=RolesListModel, status_code=status.HTTP_200_OK)
async def get_roles(
    _: CurrentUserModel | None = Security(
        OptionalAuthorization(), scopes=[ScopesEnum.ROLES_GET_ROLES.name]
    ),
    role_service: RoleService = Depends(),
) -> dict[str, Any]:
    """API which returns roles list.

    Args:
        _ (CurrentUserModel | None): Current user object or None.
        role_service (RoleService): Role service.

    Returns:
        dict[str, Any]: List of roles.

    """

    return dict(
        data=await role_service.get(),
        total=await role_service.count(),
    )
