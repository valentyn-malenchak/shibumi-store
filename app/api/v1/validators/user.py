"""Contains user domain validators."""


from typing import Any, List

from bson import ObjectId
from fastapi import Depends, HTTPException, Request, status

from app.api.v1.constants import RolesEnum
from app.api.v1.models.user import CurrentUserModel, User
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


class UserAccessValidator(BaseUserValidator):
    """User access validator."""

    async def validate(self, user_id: ObjectId) -> None:
        """Checks if the current user is the same as requested.

        Args:
            user_id (ObjectId): BSON object identifier of requested user.

        Raises:
            HTTPException: If current and requested users are different.

        """

        current_user: CurrentUserModel = self.request.state.current_user

        if current_user.object.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=HTTPErrorMessagesEnum.USER_ACCESS_DENIED,
            )


class UserIdValidator(BaseUserValidator):
    """User identifier validator."""

    async def validate(self, user_id: ObjectId) -> User:
        """Validates requested user by id.

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
                detail=HTTPErrorMessagesEnum.ENTITY_IS_NOT_FOUND.format(entity="User"),  # type: ignore
            )

        return user


class UsernameValidator(BaseUserValidator):
    """Username validator."""

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
                detail=HTTPErrorMessagesEnum.ENTITY_IS_NOT_FOUND.format(  # type: ignore
                    entity="User"
                ),
            )

        return user


class UserStatusValidator(BaseUserValidator):
    """User status validator."""

    async def validate(self, user: User) -> User:
        """Validates requested user state.

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
                detail=HTTPErrorMessagesEnum.ENTITY_IS_NOT_FOUND.format(  # type: ignore
                    entity="User"
                ),
            )

        return user


class UserRolesValidator(BaseUserValidator):
    """Roles validator class."""

    async def validate(self, roles: List[RolesEnum]) -> None:
        """Validates roles depends on current user.

        Args:
            roles (List[RolesEnum]): Roles list to validate.

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
                detail=HTTPErrorMessagesEnum.ROLE_ACCESS_DENIED,
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
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=HTTPErrorMessagesEnum.EMAIL_IS_ALREADY_VERIFIED,
            )

        return user
