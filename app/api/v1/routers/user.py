"""Module that contains user domain routers."""


from typing import Any, Dict

from fastapi import APIRouter, Depends, Security, status

from app.api.v1.auth.auth import OptionalAuthorization, StrictAuthorization
from app.api.v1.constants import ScopesEnum
from app.api.v1.dependencies.user import (
    CreateUserRolesDependency,
    DeleteUserDependency,
    UpdateUserDependency,
    UpdateUserPasswordDependency,
    UpdateUserRolesDependency,
    UserDependency,
)
from app.api.v1.models import PaginationModel, SearchModel, SortingModel
from app.api.v1.models.user import (
    CreateUserRequestModel,
    CurrentUserModel,
    UpdateUserRequestModel,
    User,
    UserPasswordUpdateModel,
    UserResponseModel,
    UsersFilterModel,
    UsersListModel,
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


@router.get("/", response_model=UsersListModel, status_code=status.HTTP_200_OK)
async def get_users(
    _: CurrentUserModel = Security(
        StrictAuthorization(), scopes=[ScopesEnum.USERS_GET_USERS.name]
    ),
    filter_: UsersFilterModel = Depends(),
    search: SearchModel = Depends(),
    sorting: SortingModel = Depends(),
    pagination: PaginationModel = Depends(),
    user_service: UserService = Depends(),
) -> Dict[str, Any]:
    """API which returns users list.

    Args:
        filter_ (UsersFilterModel): Parameters for list filtering.
        search (SearchModel): Parameters for list searching.
        sorting (SortingModel): Parameters for sorting.
        pagination (PaginationModel): Parameters for pagination.
        _: Current user object.
        user_service (UserService): User service.

    Returns:
        UsersListModel: List of user object.

    """

    return dict(
        data=await user_service.get_items(
            filter_=filter_, search=search, sorting=sorting, pagination=pagination
        ),
        total=await user_service.count_documents(filter_=filter_, search=search),
    )


@router.get(
    "/{user_id}/", response_model=UserResponseModel, status_code=status.HTTP_200_OK
)
async def get_user(
    _: CurrentUserModel = Security(
        StrictAuthorization(), scopes=[ScopesEnum.USERS_GET_USER.name]
    ),
    user: User = Depends(UserDependency()),
) -> User | None:
    """API which returns a specific user.

    Args:
        _: Current user object.
        user (User): User object.

    Returns:
        User: User object.

    """
    return user


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
    user: User = Depends(UpdateUserDependency()),
    user_data: UpdateUserRequestModel = Depends(UpdateUserRolesDependency()),
    user_service: UserService = Depends(),
) -> User | None:
    """API which updates a user object.

    Args:
        _: Current user object.
        user (User): User object.
        user_data (UpdateUserRequestModel): User data to update.
        user_service (UserService): User service.

    Returns:
        User | None: Updated user object.

    """
    return await user_service.update_item_by_id(id_=user.id, item=user_data)


@router.patch("/{user_id}/password/", status_code=status.HTTP_204_NO_CONTENT)
async def update_user_password(
    _: CurrentUserModel = Security(
        StrictAuthorization(), scopes=[ScopesEnum.USERS_UPDATE_USER_PASSWORD.name]
    ),
    user: User = Depends(UserDependency()),
    password: UserPasswordUpdateModel = Depends(UpdateUserPasswordDependency()),
    user_service: UserService = Depends(),
) -> None:
    """API which updates a user password.

    Args:
        _: Current user object.
        user (User): User object.
        password (UserPasswordUpdateModel): Old and new passwords.
        user_service (UserService): User service.

    """
    return await user_service.update_item_password(
        id_=user.id, password=password.new_password
    )


@router.delete("/{user_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    _: CurrentUserModel = Security(
        StrictAuthorization(), scopes=[ScopesEnum.USERS_DELETE_USER.name]
    ),
    user: User = Depends(DeleteUserDependency()),
    user_service: UserService = Depends(),
) -> None:
    """API which softly deletes a user object.

    Args:
        _: Current user object.
        user (User): User object.
        user_service (UserService): User service.

    """
    return await user_service.delete_item_by_id(id_=user.id)
