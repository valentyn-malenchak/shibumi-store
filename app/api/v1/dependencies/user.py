"""Contains user domain dependencies."""

from bson import ObjectId
from fastapi import Depends, HTTPException, Request, status

from app.api.v1.models.user import (
    CreateUserRequestModel,
    UpdateUserRequestModel,
)
from app.api.v1.services.user import UserService
from app.api.v1.validators import ObjectIDValidator
from app.api.v1.validators.user import (
    DeletedUserValidator,
    RolesValidator,
    UserSpecificValidator,
)
from app.constants import HTTPErrorMessagesEnum


class UserUpdateDependency:
    """User update dependency."""

    async def __call__(
        self, user_id: str, request: Request, user_service: UserService = Depends()
    ) -> ObjectId:
        """Checks if the current user can update requested user.

        Args:
            user_id (str): Identifier of requested user.
            request (Request): Current request object.
            user_service (UserService): User service.

        Returns:
            ObjectId: BSON object identifier of requested user.

        Raises:
            HTTPException: If current user can't update requested one
            or user identifier is invalid.

        """

        object_id = ObjectIDValidator.validate(id_=user_id)

        current_user = request.state.current_user

        user = await DeletedUserValidator.validate(
            object_id=object_id, user_service=user_service
        )

        if current_user.object.is_client is True:
            UserSpecificValidator.validate(current_user=current_user, user_id=user_id)

        elif user and user.is_client is True:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=HTTPErrorMessagesEnum.CLIENT_USER_ACCESS_DENIED.value,
            )

        return object_id


class UserDeleteDependency:
    """User delete dependency."""

    async def __call__(
        self, user_id: str, request: Request, user_service: UserService = Depends()
    ) -> ObjectId:
        """Checks if the current user can delete requested user.

        Args:
            user_id (str): Identifier of requested user.
            request (Request): Current request object.
            user_service (UserService): User service.

        Returns:
            ObjectId: BSON object identifier of requested user.

        Raises:
            HTTPException: If current user can't delete requested one
            or user identifier is invalid.

        """

        object_id = ObjectIDValidator.validate(id_=user_id)

        current_user = request.state.current_user

        if current_user.object.is_client is True:
            UserSpecificValidator.validate(current_user=current_user, user_id=user_id)

        await DeletedUserValidator.validate(
            object_id=object_id, user_service=user_service
        )

        return object_id


class CreateUserRolesDependency:
    """Roles dependency on user create."""

    async def __call__(
        self, user_data: CreateUserRequestModel, request: Request
    ) -> CreateUserRequestModel:
        """Validates requested user roles.

        Args:
            user_data (CreateUserRequestModel): Requested user's data.
            request (Request): Current request object.

        Returns:
            CreateUserRequestModel: Requested user's data.

        """

        current_user = getattr(request.state, "current_user", None)

        RolesValidator.validate(current_user=current_user, roles=user_data.roles)

        return user_data


class UpdateUserRolesDependency:
    """Roles dependency on user update."""

    async def __call__(
        self, user_data: UpdateUserRequestModel, request: Request
    ) -> UpdateUserRequestModel:
        """Validates requested user roles.

        Args:
            user_data (UpdateUserRequestModel): Requested user's data.
            request (Request): Current request object.

        Returns:
            UpdateUserRequestModel: Requested user's data.

        """

        current_user = request.state.current_user

        RolesValidator.validate(current_user=current_user, roles=user_data.roles)

        return user_data
