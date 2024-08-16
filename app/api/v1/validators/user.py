"""Contains user domain validators."""

from typing import Any

from bson import ObjectId
from fastapi import Depends, HTTPException, Request, status

from app.api.v1.auth.password import Password
from app.api.v1.constants import RolesEnum
from app.api.v1.models.user import CurrentUser, User
from app.api.v1.services.user import UserService
from app.api.v1.validators import BaseValidator
from app.constants import HTTPErrorMessagesEnum
from app.exceptions import EntityIsNotFoundError


class BaseUserValidator(BaseValidator):
    """Base user validator."""

    def __init__(self, request: Request, user_service: UserService = Depends()):
        """Initializes base user validator.

        Args:
            request (Request): Current request object.
            user_service (UserService): User service.

        """

        super().__init__(request=request)

        self.user_service = user_service

    async def validate(self, *args: Any) -> Any:
        """Validates data.

        Args:
            args (Any): Method arguments.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.

        """
        raise NotImplementedError


class UserByIdValidator(BaseUserValidator):
    """User by identifier validator."""

    async def validate(self, user_id: ObjectId) -> User:
        """Validates requested user by identifier.

        Args:
            user_id (ObjectId): BSON object identifier of requested user.

        Returns:
            User: User object.

        Raises:
            HTTPException: If requested user is not found.

        """

        try:
            user = await self.user_service.get_by_id(id_=user_id)

        except EntityIsNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=HTTPErrorMessagesEnum.ENTITY_IS_NOT_FOUND.format(entity="User"),
            )

        return user


class UserByUsernameValidator(BaseUserValidator):
    """User by username validator."""

    async def validate(self, username: str) -> User:
        """Validates requested user by username.

        Args:
            username (str): Username of requested user.

        Returns:
            User: User object.

        Raises:
            HTTPException: If requested user is not found.

        """

        try:
            user = await self.user_service.get_by_username(username=username)

        except EntityIsNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=HTTPErrorMessagesEnum.ENTITY_IS_NOT_FOUND.format(entity="User"),
            )

        return user


class UserStatusValidator(BaseUserValidator):
    """User status validator."""

    async def validate(self, user: User) -> User:
        """Validates if requested user is deleted.

        Args:
            user (User): User object.

        Returns:
            User: User object.

        Raises:
            HTTPException: If requested user is deleted.

        """

        if user.deleted is True:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=HTTPErrorMessagesEnum.ENTITY_IS_NOT_FOUND.format(entity="User"),
            )

        return user


class UserGetAccessValidator(BaseUserValidator):
    """User get access validator."""

    async def validate(self, user_id: ObjectId) -> None:
        """Validates if the current user is the same as requested.

        Args:
            user_id (ObjectId): BSON object identifier of requested user.

        Raises:
            HTTPException: If current and requested users are different.

        """

        current_user: CurrentUser = self.request.state.current_user

        if current_user.object.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=HTTPErrorMessagesEnum.ACCESS_DENIED.format(destination="user"),
            )


class UserUpdateAccessValidator(BaseUserValidator):
    """User update access validator."""

    def __init__(
        self,
        request: Request,
        user_service: UserService = Depends(),
        user_get_access_validator: UserGetAccessValidator = Depends(),
    ) -> None:
        """Initializes user update access validator.

        Args:
            request (Request): Current request object.
            user_service (UserService): User service.
            user_get_access_validator (UserGetAccessValidator): User get access
            validator.

        """

        super().__init__(request=request, user_service=user_service)

        self.user_get_access_validator = user_get_access_validator

    async def validate(self, user: User) -> User:
        """Validates if the current user can update user from request.

        Args:
            user (User): User object.

        Returns:
            User: User object.

        Raises:
            HTTPException: If current user can't update requested one.

        """

        current_user = self.request.state.current_user

        if current_user.object.is_client is True:
            await self.user_get_access_validator.validate(user_id=user.id)

        elif user and user.is_client is True:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=HTTPErrorMessagesEnum.ACCESS_DENIED.format(
                    destination="client user"
                ),
            )

        return user


class UserPasswordValidator(BaseUserValidator):
    """User password validator."""

    async def validate(self, old_password: str) -> None:
        """Validates old user password on update.

        Args:
            old_password (str): Old password.

        Raises:
            HTTPException: If requested and stored passwords doesn't match.

        """

        current_user = self.request.state.current_user

        if not Password.verify_password(
            plain_password=old_password,
            hashed_password=current_user.object.hashed_password,
        ):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=HTTPErrorMessagesEnum.PASSWORD_DOES_NOT_MATCH,
            )


class UserDeleteAccessValidator(BaseUserValidator):
    """User delete access validator."""

    def __init__(
        self,
        request: Request,
        user_service: UserService = Depends(),
        user_get_access_validator: UserGetAccessValidator = Depends(),
    ) -> None:
        """Initializes user delete access validator.

        Args:
            request (Request): Current request object.
            user_service (UserService): User service.
            user_get_access_validator (UserGetAccessValidator): User get access
            validator.

        """

        super().__init__(request=request, user_service=user_service)

        self.user_get_access_validator = user_get_access_validator

    async def validate(self, user: User) -> User:
        """Validates if the current user can delete requested user.

        Args:
            user (User): User object.

        Returns:
            User: User object.

        """

        current_user = self.request.state.current_user

        if current_user.object.is_client is True:
            await self.user_get_access_validator.validate(user_id=user.id)

        return user


class UserRolesValidator(BaseUserValidator):
    """Roles validator class."""

    async def validate(self, roles: list[RolesEnum]) -> None:
        """Validates roles depends on current user.

        Args:
            roles (list[RolesEnum]): Roles list to validate.

        Raises:
            HTTPException: Not permitted roles are requested.

        """

        current_user = getattr(self.request.state, "current_user", None)

        # Unauthenticated users or users with only 'Customer'
        # role can operate only with itself
        if (current_user is None or current_user.object.is_client) and roles != [
            RolesEnum.CUSTOMER
        ]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=HTTPErrorMessagesEnum.ACCESS_DENIED.format(destination="role"),
            )


class UserEmailVerifiedValidator(BaseUserValidator):
    """User email verified validator."""

    async def validate(self, user: User) -> User:
        """Validates if user email is already verified.

        Args:
            user (User): User object.

        Returns:
            User: User object.

        Raises:
            HTTPException: If requested user email is verified.

        """

        if user.email_verified is True:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=HTTPErrorMessagesEnum.EMAIL_IS_ALREADY_VERIFIED,
            )

        return user
