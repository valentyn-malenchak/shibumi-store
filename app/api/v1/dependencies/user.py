"""Contains user domain dependencies."""

from typing import Annotated

from bson import ObjectId
from fastapi import Depends, HTTPException, Request, status

from app.api.v1.auth.password import Password
from app.api.v1.models import ObjectIdAnnotation
from app.api.v1.models.user import (
    CreateUserRequestModel,
    UpdateUserRequestModel,
    User,
    UserPasswordUpdateModel,
)
from app.api.v1.validators.user import (
    UserAccessValidator,
    UserEmailVerifiedValidator,
    UserIdValidator,
    UsernameValidator,
    UserRolesValidator,
    UserStatusValidator,
)
from app.constants import HTTPErrorMessagesEnum


class UserIdDependency:
    """User identifier dependency."""

    async def __call__(
        self,
        user_id: Annotated[ObjectId, ObjectIdAnnotation],
        user_id_validator: UserIdValidator = Depends(),
    ) -> User:
        """Checks user from request by identifier.

        Args:
            user_id (Annotated[ObjectId, ObjectIdAnnotation]): BSON object
            identifier of requested user.
            user_id_validator (UserIdValidator): User identifier validator.

        Returns:
            User: User object.

        """

        return await user_id_validator.validate(user_id=user_id)


class UserStatusDependency:
    """User status dependency."""

    async def __call__(
        self,
        user: User = Depends(UserIdDependency()),
        user_status_validator: UserStatusValidator = Depends(),
    ) -> User:
        """Checks user status.

        Args:
            user (User): User object.
            user_status_validator (UserStatusValidator): User status validator.

        Returns:
            User: User object.

        """
        return await user_status_validator.validate(user=user)


class UsernameDependency:
    """Username dependency."""

    async def __call__(
        self,
        username: str,
        username_validator: UsernameValidator = Depends(),
        user_status_validator: UserStatusValidator = Depends(),
    ) -> User:
        """Checks user from request by username.

        Args:
            username (str): Username of requested user.
            username_validator (UsernameValidator): Username validator.
            user_status_validator (UserStatusValidator): User status validator.

        Returns:
            User: User object.

        """

        user = await username_validator.validate(username=username)

        return await user_status_validator.validate(user=user)


class UpdateUserDependency:
    """Update user dependency."""

    async def __call__(
        self,
        request: Request,
        user: User = Depends(UserStatusDependency()),
        user_access_validator: UserAccessValidator = Depends(),
    ) -> User:
        """Checks if the current user can update user from request.

        Args:
            request (Request): Current request object.
            user (User): User object.
            user_access_validator (UserAccessValidator): User access validator.

        Returns:
            User: User object.

        Raises:
            HTTPException: If current user can't update requested one
            or user identifier is invalid.

        """

        current_user = request.state.current_user

        if current_user.object.is_client is True:
            await user_access_validator.validate(user_id=user.id)

        elif user and user.is_client is True:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=HTTPErrorMessagesEnum.CLIENT_USER_ACCESS_DENIED,
            )

        return user


class UpdateUserPasswordDependency:
    """Update user password dependency."""

    async def __call__(
        self,
        user_id: Annotated[ObjectId, ObjectIdAnnotation],
        request: Request,
        password: UserPasswordUpdateModel,
        user_access_validator: UserAccessValidator = Depends(),
    ) -> UserPasswordUpdateModel:
        """Checks if the current user can update own password.

        Args:
            user_id (Annotated[ObjectId, ObjectIdAnnotation]): BSON object
            identifier of requested user.
            request (Request): Current request object.
            password (UserPasswordUpdateModel): Old and new passwords.
            user_access_validator (UserAccessValidator): User access validator.

        Returns:
            UserPasswordUpdateModel: Old and new passwords.

        Raises:
            HTTPException: If old and new passwords doesn't match.

        """

        current_user = request.state.current_user

        # User can update only own password
        await user_access_validator.validate(user_id=user_id)

        if not Password.verify_password(
            plain_password=password.old_password,
            hashed_password=current_user.object.hashed_password,
        ):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=HTTPErrorMessagesEnum.PASSWORD_DOES_NOT_MATCH,
            )

        return password


class DeleteUserDependency:
    """Delete user dependency."""

    async def __call__(
        self,
        request: Request,
        user: User = Depends(UserStatusDependency()),
        user_access_validator: UserAccessValidator = Depends(),
    ) -> User:
        """Checks if the current user can delete requested user.

        Args:
            request (Request): Current request object.
            user (User): User object.
            user_access_validator (UserAccessValidator): User access validator.

        Returns:
            User: User object.

        Raises:
            HTTPException: If current user can't delete requested one
            or user identifier is invalid.

        """

        current_user = request.state.current_user

        if current_user.object.is_client is True:
            await user_access_validator.validate(user_id=user.id)

        return user


class CreateUserRolesDependency:
    """Roles dependency on user create."""

    async def __call__(
        self,
        user_data: CreateUserRequestModel,
        user_roles_validator: UserRolesValidator = Depends(),
    ) -> CreateUserRequestModel:
        """Validates requested user roles.

        Args:
            user_data (CreateUserRequestModel): Requested user's data.
            user_roles_validator (UserRolesValidator): Roles validator.

        Returns:
            CreateUserRequestModel: Requested user's data.

        """

        await user_roles_validator.validate(roles=user_data.roles)

        return user_data


class UpdateUserRolesDependency:
    """Roles dependency on user update."""

    async def __call__(
        self,
        user_data: UpdateUserRequestModel,
        user_roles_validator: UserRolesValidator = Depends(),
    ) -> UpdateUserRequestModel:
        """Validates requested user roles.

        Args:
            user_data (UpdateUserRequestModel): Requested user's data.
            user_roles_validator (UserRolesValidator): Roles validator.

        Returns:
            UpdateUserRequestModel: Requested user's data.

        """

        await user_roles_validator.validate(roles=user_data.roles)

        return user_data


class VerifyUserEmailDependency:
    """Verify user email dependency"""

    async def __call__(
        self,
        username: str,
        user: User = Depends(UsernameDependency()),
        user_email_verification_validator: UserEmailVerifiedValidator = Depends(),
    ) -> User:
        """Checks user from request.

        Args:
            username (str): Username of requested user.
            user (User): User object.
            user_email_verification_validator (UserEmailVerifiedValidator): User email
            verification validator.

        Returns:
            User: User object.

        """

        return await user_email_verification_validator.validate(user=user)
