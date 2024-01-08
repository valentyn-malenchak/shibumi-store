"""Module that contains users domain routers."""


from bson import ObjectId
from fastapi import APIRouter, Depends, Security, status

from app.api.v1.auth.auth import OptionalAuthorization, StrictAuthorization
from app.api.v1.constants import ScopesEnum
from app.api.v1.dependencies.users import (
    CreateUserRolesDependency,
    UpdateUserRolesDependency,
    UserDeleteDependency,
    UserUpdateDependency,
)
from app.api.v1.models.users import (
    CreateUserRequestModel,
    CurrentUserModel,
    UpdateUserRequestModel,
    User,
    UserResponseModel,
)
from app.api.v1.services.users import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me/", response_model=UserResponseModel, status_code=status.HTTP_200_OK)
async def get_users_me(
    current_user: CurrentUserModel = Security(
        StrictAuthorization(), scopes=[ScopesEnum.USERS_GET_ME.name]
    ),
) -> User:
    """API which returns current user object.

    Args:
        current_user (CurrentUserModel): Current authorized user with permitted scopes.

    Returns:
        User: Current user object.

    """
    return current_user.object


@router.post("/", response_model=UserResponseModel, status_code=status.HTTP_201_CREATED)
async def create_users(
    _: CurrentUserModel | None = Security(
        OptionalAuthorization(), scopes=[ScopesEnum.USERS_CREATE_USERS.name]
    ),
    user_data: CreateUserRequestModel = Depends(CreateUserRolesDependency()),
    user_service: UserService = Depends(),
) -> User | None:
    """API which creates a new user.

    Args:
        user_data (CreateUserRequestModel): User registration data.
        _ (CurrentUserModel | None): Authenticated user with permitted scopes or None.
        user_service (UserService): User service.

    Returns:
        User | None: Created user object.

    """
    return await user_service.create_item(item=user_data)


@router.patch(
    "/{user_id}/", response_model=UserResponseModel, status_code=status.HTTP_200_OK
)
async def update_users(
    _: CurrentUserModel = Security(
        StrictAuthorization(), scopes=[ScopesEnum.USERS_UPDATE_USERS.name]
    ),
    user_id: ObjectId = Depends(UserUpdateDependency()),
    user_data: UpdateUserRequestModel = Depends(UpdateUserRolesDependency()),
    user_service: UserService = Depends(),
) -> User | None:
    """API which updates a user object.

    Args:
        user_data (UpdateUserRequestModel): User data to update.
        _: Current user object.
        user_id (str): Identifier of user that should be updated.
        user_service (UserService): User service.

    Returns:
        User | None: Updated user object.

    """
    return await user_service.update_item_by_id(id_=user_id, item=user_data)


@router.delete("/{user_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_users(
    _: CurrentUserModel = Security(
        StrictAuthorization(), scopes=[ScopesEnum.USERS_DELETE_USERS.name]
    ),
    user_id: ObjectId = Depends(UserDeleteDependency()),
    user_service: UserService = Depends(),
) -> None:
    """API which softly deletes a user object.

    Args:
        _: Current user object.
        user_id (str): Identifier of user that should be deleted.
        user_service (UserService): User service.

    """
    return await user_service.delete_item_by_id(id_=user_id)
