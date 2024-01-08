"""Contains user domain validators."""


from typing import List

from fastapi import HTTPException, Request, status

from app.api.v1.constants import RolesEnum
from app.api.v1.models.users import (
    CreateUserRequestModel,
    CurrentUserModel,
    UpdateUserRequestModel,
)
from app.api.v1.validators import BaseValidator, ObjectIDValidator
from app.constants import HTTPErrorMessagesEnum


class UserSpecificDependency:
    """Specific user operations dependency."""

    async def __call__(self, user_id: str, request: Request) -> str:
        """Checks if the current user can operate requested user.

        Args:
            user_id (str): Identifier of requested user.
            request (Request): Current request object.

        Returns:
            str: Identifier of requested user.

        Raises:
            HTTPException: If current and requested users are different
            or user identifier is invalid.

        """

        ObjectIDValidator.validate(id_=user_id)

        current_user = request.state.current_user

        if current_user.object.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=HTTPErrorMessagesEnum.USER_ACCESS_DENIED.value,
            )

        return user_id


class RolesValidator(BaseValidator):
    """Roles validator class."""

    @classmethod
    def validate(
        cls, current_user: CurrentUserModel | None, roles: List[RolesEnum]
    ) -> None:
        """Validates roles depends on current user.

        Args:
            current_user (CurrentUserModel | None): Current authorized
            user with permitted scopes.
            roles (List[RolesEnum]): Roles list to validate.

        """

        # Unauthenticated users or users with only 'Customer'
        # role can operate only with it
        if (
            current_user is None
            or current_user.object.roles == [RolesEnum.CUSTOMER.name]
        ) and roles != [RolesEnum.CUSTOMER]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=HTTPErrorMessagesEnum.ROLE_ACCESS_DENIED.value,
            )


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
