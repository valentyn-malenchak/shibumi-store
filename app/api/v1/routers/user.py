"""Module that contains user domain routers."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, Security, status

from app.api.v1.auth.auth import OptionalAuthorization, StrictAuthorization
from app.api.v1.constants import ScopesEnum
from app.api.v1.dependencies.user import (
    UserByIdGetDependency,
    UserByUsernameStatusGetDependency,
    UserDataCreateDependency,
    UserDataUpdateDependency,
    UserDeleteAccessDependency,
    UserEmailVerifiedDependency,
    UserGetAccessDependency,
    UserPasswordDataUpdateDependency,
    UserUpdateAccessDependency,
)
from app.api.v1.models import Pagination, Search, Sorting
from app.api.v1.models.user import (
    BaseUserCreateData,
    BaseUserUpdateData,
    CurrentUser,
    ShortUser,
    User,
    UserFilter,
    UserList,
    UserPasswordResetData,
    UserPasswordUpdateData,
    VerificationToken,
)
from app.api.v1.services.user import UserService
from app.constants import HTTPErrorMessagesEnum
from app.exceptions import EntityDuplicateKeyError, InvalidVerificationTokenError

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me/", response_model=ShortUser, status_code=status.HTTP_200_OK)
async def get_user_me(
    current_user: CurrentUser = Security(
        StrictAuthorization(), scopes=[ScopesEnum.USERS_GET_ME.name]
    ),
) -> User:
    """API which returns current user object.

    Args:
        current_user (CurrentUser): Current authorized user with permitted scopes.

    Returns:
        User: Current user object.

    """
    return current_user.object


@router.get(
    "/",
    response_model=UserList,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Security(StrictAuthorization(), scopes=[ScopesEnum.USERS_GET_USERS.name])
    ],
)
async def get_users(
    filter_: Annotated[UserFilter, Query()],
    search: Search = Depends(),
    sorting: Sorting = Depends(),
    pagination: Pagination = Depends(),
    user_service: UserService = Depends(),
) -> dict[str, Any]:
    """API which returns users list.

    Args:
        filter_ (UserFilter): Parameters for list filtering.
        search (Search): Parameters for list searching.
        sorting (Sorting): Parameters for sorting.
        pagination (Pagination): Parameters for pagination.
        user_service (UserService): User service.

    Returns:
        UserList: List of users object.

    """
    return dict(
        data=await user_service.get(
            filter_=filter_, search=search, sorting=sorting, pagination=pagination
        ),
        total=await user_service.count(filter_=filter_, search=search),
    )


@router.get(
    "/{user_id}/",
    response_model=ShortUser,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Security(StrictAuthorization(), scopes=[ScopesEnum.USERS_GET_USER.name])
    ],
)
async def get_user(user: User = Depends(UserByIdGetDependency())) -> User:
    """API which returns a specific user.

    Args:
        user (User): User object.

    Returns:
        User: User object.

    """
    return user


@router.post(
    "/",
    response_model=ShortUser,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Security(OptionalAuthorization(), scopes=[ScopesEnum.USERS_CREATE_USER.name])
    ],
)
async def create_user(
    user_data: BaseUserCreateData = Depends(UserDataCreateDependency()),
    user_service: UserService = Depends(),
) -> User:
    """API which creates a new user.

    Args:
        user_data (BaseUserCreateData): User registration data.
        user_service (UserService): User service.

    Returns:
        User: Created user object.

    Raises:
        HTTPException: in case user with such username is already exists.

    """
    try:
        return await user_service.create(data=user_data)

    except EntityDuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=HTTPErrorMessagesEnum.ENTITY_FIELD_UNIQUENESS.format(
                entity="User", field="username"
            ),
        )


@router.post("/{username}/verify-email/", status_code=status.HTTP_204_NO_CONTENT)
async def request_verify_user_email(
    user: User = Depends(UserEmailVerifiedDependency()),
    user_service: UserService = Depends(),
) -> None:
    """API which requests user's email verification.

    Args:
        user (User): User object.
        user_service (UserService): User service.

    """
    return await user_service.request_verify_email(item=user)


@router.patch("/{username}/verify-email/", status_code=status.HTTP_204_NO_CONTENT)
async def verify_user_email(
    verify_email: VerificationToken,
    user: User = Depends(UserEmailVerifiedDependency()),
    user_service: UserService = Depends(),
) -> None:
    """API which verifies user's email.

    Args:
        verify_email (VerificationToken): Email verification token.
        user (User): User object.
        user_service (UserService): User service.

    Raises:
        HTTPException: in case email verification token is invalid.

    """
    try:
        return await user_service.verify_email(id_=user.id, token=verify_email.token)

    except InvalidVerificationTokenError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=HTTPErrorMessagesEnum.INVALID_EMAIL_VERIFICATION_TOKEN,
        )


@router.patch(
    "/{user_id}/",
    response_model=ShortUser,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Security(StrictAuthorization(), scopes=[ScopesEnum.USERS_UPDATE_USER.name])
    ],
)
async def update_user(
    user: User = Depends(UserUpdateAccessDependency()),
    user_data: BaseUserUpdateData = Depends(UserDataUpdateDependency()),
    user_service: UserService = Depends(),
) -> User:
    """API which updates a user object.

    Args:
        user (User): User object.
        user_data (BaseUserUpdateData): User data to update.
        user_service (UserService): User service.

    Returns:
        User: Updated user object.

    """
    return await user_service.update(item=user, data=user_data)


@router.patch(
    "/{user_id}/password/",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Security(
            StrictAuthorization(), scopes=[ScopesEnum.USERS_UPDATE_USER_PASSWORD.name]
        )
    ],
)
async def update_user_password(
    user: User = Depends(UserGetAccessDependency()),
    password: UserPasswordUpdateData = Depends(UserPasswordDataUpdateDependency()),
    user_service: UserService = Depends(),
) -> None:
    """API which updates a user password.

    Args:
        user (User): User object.
        password (UserPasswordUpdateData): Old and new passwords.
        user_service (UserService): User service.

    """
    return await user_service.update_password(
        id_=user.id, password=password.new_password
    )


@router.delete(
    "/{user_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Security(StrictAuthorization(), scopes=[ScopesEnum.USERS_DELETE_USER.name])
    ],
)
async def delete_user(
    user: User = Depends(UserDeleteAccessDependency()),
    user_service: UserService = Depends(),
) -> None:
    """API which softly deletes a user object.

    Args:
        user (User): User object.
        user_service (UserService): User service.

    """
    return await user_service.delete_by_id(id_=user.id)


@router.post("/{username}/reset-password/", status_code=status.HTTP_204_NO_CONTENT)
async def request_reset_user_password(
    user: User = Depends(UserByUsernameStatusGetDependency()),
    user_service: UserService = Depends(),
) -> None:
    """API which requests reset password.

    Args:
        user (User): User object.
        user_service (UserService): User service.

    """
    return await user_service.request_reset_password(item=user)


@router.patch("/{username}/reset-password/", status_code=status.HTTP_204_NO_CONTENT)
async def reset_user_password(
    reset_password: UserPasswordResetData,
    user: User = Depends(UserByUsernameStatusGetDependency()),
    user_service: UserService = Depends(),
) -> None:
    """API which resets password.

    Args:
        reset_password (UserPasswordResetData): Reset token with new password.
        user (User): User object.
        user_service (UserService): User service.

    Raises:
        HTTPException: in case reset password token is invalid.

    """
    try:
        return await user_service.reset_password(
            id_=user.id,
            token=reset_password.token,
            password=reset_password.new_password,
        )

    except InvalidVerificationTokenError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=HTTPErrorMessagesEnum.INVALID_RESET_PASSWORD_TOKEN,
        )
