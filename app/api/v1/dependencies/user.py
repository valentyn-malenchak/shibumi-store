"""Contains user domain dependencies."""

from typing import Annotated

from bson import ObjectId
from fastapi import Depends

from app.api.v1.models.user import (
    BaseUserCreateData,
    BaseUserUpdateData,
    User,
    UserPasswordUpdateData,
)
from app.api.v1.validators.user import (
    UserByIdValidator,
    UserByUsernameStatusValidator,
    UserDeleteAccessValidator,
    UserEmailVerifiedValidator,
    UserPasswordUpdateValidator,
    UserRolesValidator,
    UserUpdateAccessValidator,
)
from app.utils.pydantic import ObjectIdAnnotation


class UserByIdDependency:
    """User by identifier dependency."""

    async def __call__(
        self,
        user_id: Annotated[ObjectId, ObjectIdAnnotation],
        user_by_id_validator: UserByIdValidator = Depends(),
    ) -> User:
        """Validates user from request by identifier.

        Args:
            user_id (Annotated[ObjectId, ObjectIdAnnotation]): BSON object
            identifier of requested user.
            user_by_id_validator (UserByIdValidator): User by identifier validator.

        Returns:
            User: User object.

        """

        return await user_by_id_validator.validate(user_id=user_id)


class UserByUsernameStatusDependency:
    """User by username status dependency."""

    async def __call__(
        self,
        username: str,
        user_by_username_status_validator: UserByUsernameStatusValidator = Depends(),
    ) -> User:
        """Validates user and its status from request by username.

        Args:
            username (str): Username of requested user.
            user_by_username_status_validator (UserByUsernameStatusValidator): User
            by username status validator.

        Returns:
            User: User object.

        """

        return await user_by_username_status_validator.validate(username=username)


class UserUpdateAccessDependency:
    """User update access dependency."""

    async def __call__(
        self,
        user_id: Annotated[ObjectId, ObjectIdAnnotation],
        user_update_access_validator: UserUpdateAccessValidator = Depends(),
    ) -> User:
        """Validates if the current user can update user from request.

        Args:
            user_id (Annotated[ObjectId, ObjectIdAnnotation]): BSON object
            identifier of requested user.
            user_update_access_validator (UserUpdateAccessValidator): User update access
            validator.

        Returns:
            User: User object.

        """

        return await user_update_access_validator.validate(user_id=user_id)


class UserPasswordUpdateDependency:
    """User password update dependency."""

    async def __call__(
        self,
        user_id: Annotated[ObjectId, ObjectIdAnnotation],
        password: UserPasswordUpdateData,
        user_password_update_validator: UserPasswordUpdateValidator = Depends(),
    ) -> UserPasswordUpdateData:
        """Validates if the current user can update own password.

        Args:
            user_id (Annotated[ObjectId, ObjectIdAnnotation]): BSON object
            identifier of requested user.
            password (UserPasswordUpdateData): Old and new passwords.
            user_password_update_validator (UserPasswordUpdateValidator): User password
            update validator.

        Returns:
            UserPasswordUpdateData: Old and new passwords.

        """

        await user_password_update_validator.validate(
            user_id=user_id, old_password=password.old_password
        )

        return password


class UserDeleteAccessDependency:
    """User delete access dependency."""

    async def __call__(
        self,
        user_id: Annotated[ObjectId, ObjectIdAnnotation],
        user_delete_access_validator: UserDeleteAccessValidator = Depends(),
    ) -> User:
        """Validates if the current user can delete requested user.

        Args:
            user_id (Annotated[ObjectId, ObjectIdAnnotation]): BSON object
            identifier of requested user.
            user_delete_access_validator (UserDeleteAccessValidator): User delete access
            validator.

        Returns:
            User: User object.

        """

        return await user_delete_access_validator.validate(user_id=user_id)


class UserDataCreateDependency:
    """User data create dependency."""

    async def __call__(
        self,
        user_data: BaseUserCreateData,
        user_roles_validator: UserRolesValidator = Depends(),
    ) -> BaseUserCreateData:
        """Validates data on user create operation.

        Args:
            user_data (BaseUserCreateData): Base user create data.
            user_roles_validator (UserRolesValidator): Roles validator.

        Returns:
            BaseUserCreateData: Base user create data.

        """

        await user_roles_validator.validate(roles=user_data.roles)

        return user_data


class UserDataUpdateDependency:
    """User data update dependency."""

    async def __call__(
        self,
        user_data: BaseUserUpdateData,
        user_roles_validator: UserRolesValidator = Depends(),
    ) -> BaseUserUpdateData:
        """Validates data on user update operation.

        Args:
            user_data (BaseUserUpdateData): Base user update data.
            user_roles_validator (UserRolesValidator): Roles validator.

        Returns:
            BaseUserUpdateData: Base user update data.

        """

        await user_roles_validator.validate(roles=user_data.roles)

        return user_data


class UserEmailVerifiedDependency:
    """User email verified dependency."""

    async def __call__(
        self,
        username: str,
        user_email_verified_validator: UserEmailVerifiedValidator = Depends(),
    ) -> User:
        """Validates user from request.

        Args:
            username (str): Username of requested user.
            user_email_verified_validator (UserEmailVerifiedValidator): User email
            verified validator.

        Returns:
            User: User object.

        """

        return await user_email_verified_validator.validate(username=username)
