"""Contains user domain dependencies."""

from typing import Annotated

from bson import ObjectId
from fastapi import Depends

from app.api.v1.models.user import (
    User,
    UserCreateData,
    UserPasswordUpdateData,
    UserUpdateData,
)
from app.api.v1.validators.user import (
    UserByIdValidator,
    UserByUsernameStatusValidator,
    UserDeleteValidator,
    UserEmailVerifiedValidator,
    UserPasswordUpdateValidator,
    UserRolesValidator,
    UserUpdateValidator,
)
from app.utils.pydantic import ObjectIdAnnotation


class UserByIdDependency:
    """User by identifier dependency."""

    async def __call__(
        self,
        user_id: Annotated[ObjectId, ObjectIdAnnotation],
        user_by_id_validator: UserByIdValidator = Depends(),
    ) -> User:
        """Checks user from request by identifier.

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
        """Checks user and its status from request by username.

        Args:
            username (str): Username of requested user.
            user_by_username_status_validator (UserByUsernameStatusValidator): User
            by username status validator.

        Returns:
            User: User object.

        """

        return await user_by_username_status_validator.validate(username=username)


class UserUpdateDependency:
    """User update dependency."""

    async def __call__(
        self,
        user_id: Annotated[ObjectId, ObjectIdAnnotation],
        user_update_validator: UserUpdateValidator = Depends(),
    ) -> User:
        """Checks if the current user can update user from request.

        Args:
            user_id (Annotated[ObjectId, ObjectIdAnnotation]): BSON object
            identifier of requested user.
            user_update_validator (UserUpdateValidator): User update validator.

        Returns:
            User: User object.

        """

        return await user_update_validator.validate(user_id=user_id)


class UserPasswordUpdateDependency:
    """User password update dependency."""

    async def __call__(
        self,
        user_id: Annotated[ObjectId, ObjectIdAnnotation],
        password: UserPasswordUpdateData,
        user_password_update_validator: UserPasswordUpdateValidator = Depends(),
    ) -> UserPasswordUpdateData:
        """Checks if the current user can update own password.

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


class UserDeleteDependency:
    """User delete dependency."""

    async def __call__(
        self,
        user_id: Annotated[ObjectId, ObjectIdAnnotation],
        user_delete_validator: UserDeleteValidator = Depends(),
    ) -> User:
        """Checks if the current user can delete requested user.

        Args:
            user_id (Annotated[ObjectId, ObjectIdAnnotation]): BSON object
            identifier of requested user.
            user_delete_validator (UserDeleteValidator): User delete validator.

        Returns:
            User: User object.

        """

        return await user_delete_validator.validate(user_id=user_id)


class UserDataCreateDependency:
    """User data create dependency."""

    async def __call__(
        self,
        user_data: UserCreateData,
        user_roles_validator: UserRolesValidator = Depends(),
    ) -> UserCreateData:
        """Validates data on user create operation.

        Args:
            user_data (UserCreateData): Requested user's data.
            user_roles_validator (UserRolesValidator): Roles validator.

        Returns:
            UserCreateData: Requested user's data.

        """

        await user_roles_validator.validate(roles=user_data.roles)

        return user_data


class UserDataUpdateDependency:
    """User data update dependency."""

    async def __call__(
        self,
        user_data: UserUpdateData,
        user_roles_validator: UserRolesValidator = Depends(),
    ) -> UserUpdateData:
        """Validates data on user update operation.

        Args:
            user_data (UserUpdateData): Requested user's data.
            user_roles_validator (UserRolesValidator): Roles validator.

        Returns:
            UserUpdateData: Requested user's data.

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
        """Checks user from request.

        Args:
            username (str): Username of requested user.
            user_email_verified_validator (UserEmailVerifiedValidator): User email
            verified validator.

        Returns:
            User: User object.

        """

        return await user_email_verified_validator.validate(username=username)
