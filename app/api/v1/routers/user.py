"""Module that contains user domain routers."""


from bson import ObjectId
from fastapi import APIRouter, Depends, Security, status

from app.api.v1.auth.auth import OptionalAuthorization, StrictAuthorization
from app.api.v1.constants import ScopesEnum
from app.api.v1.dependencies.user import (
    CreateUserRolesDependency,
    UpdateUserRolesDependency,
    UserDeleteDependency,
    UserGetDependency,
    UserUpdateDependency,
)
from app.api.v1.models.user import (
    CreateUserRequestModel,
    CurrentUserModel,
    UpdateUserRequestModel,
    User,
    UserResponseModel,
)
from app.api.v1.services.user import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me/", response_model=UserResponseModel, status_code=status.HTTP_200_OK)
async def get_user_me(
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


@router.get(
    "/{user_id}/", response_model=UserResponseModel, status_code=status.HTTP_200_OK
)
async def get_user(
    _: CurrentUserModel | None = Security(
        StrictAuthorization(), scopes=[ScopesEnum.USERS_GET_USER.name]
    ),
    user_id: ObjectId = Depends(UserGetDependency()),
    user_service: UserService = Depends(),
) -> User | None:
    """API which returns a specific user.

    Args:
        _: Current user object.
        user_id (str): Identifier of user that should be returned.
        user_service (UserService): User service.

    Returns:
        User | None: User object.

    """
    return await user_service.get_item_by_id(id_=user_id)


@router.post("/", response_model=UserResponseModel, status_code=status.HTTP_201_CREATED)
async def create_user(
    _: CurrentUserModel | None = Security(
        OptionalAuthorization(), scopes=[ScopesEnum.USERS_CREATE_USER.name]
    ),
    user_data: CreateUserRequestModel = Depends(CreateUserRolesDependency()),
    user_service: UserService = Depends(),
) -> User | None:
    """API which creates a new user.

    Args:
        _ (CurrentUserModel | None): Authenticated user with permitted scopes or None.
        user_data (CreateUserRequestModel): User registration data.
        user_service (UserService): User service.

    Returns:
        User | None: Created user object.

    """
    return await user_service.create_item(item=user_data)


@router.patch(
    "/{user_id}/", response_model=UserResponseModel, status_code=status.HTTP_200_OK
)
async def update_user(
    _: CurrentUserModel = Security(
        StrictAuthorization(), scopes=[ScopesEnum.USERS_UPDATE_USER.name]
    ),
    user_id: ObjectId = Depends(UserUpdateDependency()),
    user_data: UpdateUserRequestModel = Depends(UpdateUserRolesDependency()),
    user_service: UserService = Depends(),
) -> User | None:
    """API which updates a user object.

    Args:
        _: Current user object.
        user_id (str): Identifier of user that should be updated.
        user_data (UpdateUserRequestModel): User data to update.
        user_service (UserService): User service.

    Returns:
        User | None: Updated user object.

    """
    return await user_service.update_item_by_id(id_=user_id, item=user_data)


@router.delete("/{user_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    _: CurrentUserModel = Security(
        StrictAuthorization(), scopes=[ScopesEnum.USERS_DELETE_USER.name]
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
