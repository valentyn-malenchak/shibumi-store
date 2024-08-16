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
    UserByUsernameValidator,
    UserDeleteAccessValidator,
    UserEmailVerifiedValidator,
    UserGetAccessValidator,
    UserPasswordValidator,
    UserRolesValidator,
    UserStatusValidator,
    UserUpdateAccessValidator,
)
from app.utils.metas import SingletonMeta
from app.utils.pydantic import ObjectIdAnnotation


class UserByIdGetDependency(metaclass=SingletonMeta):
    """User by identifier get dependency."""

    async def __call__(
        self,
        user_id: Annotated[ObjectId, ObjectIdAnnotation],
        user_by_id_validator: UserByIdValidator = Depends(),
    ) -> User:
        """Validates user by its unique identifier.

        Args:
            user_id (Annotated[ObjectId, ObjectIdAnnotation]): BSON object
            identifier of requested user.
            user_by_id_validator (UserByIdValidator): User by identifier validator.

        Returns:
            User: User object.

        """
        return await user_by_id_validator.validate(user_id=user_id)


class UserGetAccessDependency(metaclass=SingletonMeta):
    """User get access dependency."""

    async def __call__(
        self,
        user: User = Depends(UserByIdGetDependency()),
        user_get_access_validator: UserGetAccessValidator = Depends(),
    ) -> User:
        """Validates access to a specific user on get operation.

        Args:
            user (User): User object.
            user_get_access_validator (UserGetAccessValidator): User get access
            validator.

        Returns:
            User: User object.

        """

        await user_get_access_validator.validate(user_id=user.id)

        return user


class UserByUsernameGetDependency(metaclass=SingletonMeta):
    """User by username get dependency."""

    async def __call__(
        self,
        username: str,
        user_by_username_validator: UserByUsernameValidator = Depends(),
    ) -> User:
        """Validates user by its username.

        Args:
            username (str): Username of requested user.
            user_by_username_validator (UserByUsernameValidator): User by username
            validator.

        Returns:
            User: User object.

        """
        return await user_by_username_validator.validate(username=username)


class UserByIdStatusGetDependency(metaclass=SingletonMeta):
    """User by identifier status get dependency."""

    async def __call__(
        self,
        user: User = Depends(UserByIdGetDependency()),
        user_status_validator: UserStatusValidator = Depends(),
    ) -> User:
        """Validates user status from request by identifier.

        Args:
            user (User): User object.
            user_status_validator (UserStatusValidator): User status validator.

        Returns:
            User: User object.

        """
        return await user_status_validator.validate(user=user)


class UserByUsernameStatusGetDependency(metaclass=SingletonMeta):
    """User by username status get dependency."""

    async def __call__(
        self,
        user: User = Depends(UserByUsernameGetDependency()),
        user_status_validator: UserStatusValidator = Depends(),
    ) -> User:
        """Validates user status from request by username.

        Args:
            user (User): User object.
            user_status_validator (UserStatusValidator): User status validator.

        Returns:
            User: User object.

        """
        return await user_status_validator.validate(user=user)


class UserDataCreateDependency(metaclass=SingletonMeta):
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


class UserUpdateAccessDependency(metaclass=SingletonMeta):
    """User update access dependency."""

    async def __call__(
        self,
        user: User = Depends(UserByIdStatusGetDependency()),
        user_update_access_validator: UserUpdateAccessValidator = Depends(),
    ) -> User:
        """Validates if the current user can update user from request.

        Args:
            user (User): User object.
            user_update_access_validator (UserUpdateAccessValidator): User update access
            validator.

        Returns:
            User: User object.

        """
        return await user_update_access_validator.validate(user=user)


class UserDataUpdateDependency(metaclass=SingletonMeta):
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


class UserPasswordDataUpdateDependency(metaclass=SingletonMeta):
    """User password data update dependency."""

    async def __call__(
        self,
        password: UserPasswordUpdateData,
        user: User = Depends(UserGetAccessDependency()),
        user_password_validator: UserPasswordValidator = Depends(),
    ) -> UserPasswordUpdateData:
        """Validates passwords on update operation.

        Args:
            password (UserPasswordUpdateData): Old and new passwords.
            user (User): User object.
            user_password_validator (UserPasswordValidator): User password validator.

        Returns:
            UserPasswordUpdateData: Old and new passwords.

        """

        await user_password_validator.validate(old_password=password.old_password)

        return password


class UserDeleteAccessDependency(metaclass=SingletonMeta):
    """User delete access dependency."""

    async def __call__(
        self,
        user: User = Depends(UserByIdStatusGetDependency()),
        user_delete_access_validator: UserDeleteAccessValidator = Depends(),
    ) -> User:
        """Validates if the current user can delete requested user.

        Args:
            user (User): User object.
            user_delete_access_validator (UserDeleteAccessValidator): User delete access
            validator.

        Returns:
            User: User object.

        """
        return await user_delete_access_validator.validate(user=user)


class UserEmailVerifiedDependency(metaclass=SingletonMeta):
    """User email verified dependency."""

    async def __call__(
        self,
        user: User = Depends(UserByUsernameStatusGetDependency()),
        user_email_verified_validator: UserEmailVerifiedValidator = Depends(),
    ) -> User:
        """Verifies user from request.

        Args:
            user (User): User object.
            user_email_verified_validator (UserEmailVerifiedValidator): User email
            verified validator.

        Returns:
            User: User object.

        """
        return await user_email_verified_validator.validate(user=user)
