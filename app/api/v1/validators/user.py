"""Contains user domain validators."""

from typing import Any

from bson import ObjectId
from fastapi import Depends, HTTPException, Request, status

from app.api.v1.auth.password import Password
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


class UserByIdValidator(BaseUserValidator):
    """User by identifier validator."""

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


class UserByIdStatusValidator(BaseUserValidator):
    """User by identifier status validator."""

    def __init__(
        self,
        request: Request,
        user_service: UserService = Depends(),
        user_by_id_validator: UserByIdValidator = Depends(),
        user_status_validator: UserStatusValidator = Depends(),
    ) -> None:
        """Initializes user by identifier status validator.

        Args:
            request (Request): Current request object.
            user_service (UserService): User service.
            user_by_id_validator (UserByIdValidator): User by identifier validator.
            user_status_validator (UserStatusValidator): User status validator.

        """

        super().__init__(request=request, user_service=user_service)

        self.user_by_id_validator = user_by_id_validator

        self.user_status_validator = user_status_validator

    async def validate(self, user_id: ObjectId) -> User:
        """Validates requested user by id and its status.

        Args:
            user_id (ObjectId): BSON object identifier of requested user.

        Returns:
            User: User object.

        """

        user = await self.user_by_id_validator.validate(user_id=user_id)

        return await self.user_status_validator.validate(user=user)


class UserByUsernameStatusValidator(BaseUserValidator):
    """User by username status validator."""

    def __init__(
        self,
        request: Request,
        user_service: UserService = Depends(),
        user_by_username_validator: UserByUsernameValidator = Depends(),
        user_status_validator: UserStatusValidator = Depends(),
    ) -> None:
        """Initializes user by username status validator.

        Args:
            request (Request): Current request object.
            user_service (UserService): User service.
            user_by_username_validator (UserByUsernameValidator): User by username
            validator.
            user_status_validator (UserStatusValidator): User status validator.

        """

        super().__init__(request=request, user_service=user_service)

        self.user_by_username_validator = user_by_username_validator

        self.user_status_validator = user_status_validator

    async def validate(self, username: str) -> User:
        """Validates requested user by username and its status.

        Args:
            username (str): Username of requested user.

        Returns:
            User: User object.

        """

        user = await self.user_by_username_validator.validate(username=username)

        return await self.user_status_validator.validate(user=user)


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


class UserUpdateValidator(BaseUserValidator):
    """User update validator."""

    def __init__(
        self,
        request: Request,
        user_service: UserService = Depends(),
        user_by_id_status_validator: UserByIdStatusValidator = Depends(),
        user_access_validator: UserAccessValidator = Depends(),
    ) -> None:
        """Initializes user update validator.

        Args:
            request (Request): Current request object.
            user_service (UserService): User service.
            user_by_id_status_validator (UserByIdStatusValidator): User by id status
            validator.
            user_access_validator (UserAccessValidator): User access validator.

        """

        super().__init__(request=request, user_service=user_service)

        self.user_by_id_status_validator = user_by_id_status_validator

        self.user_access_validator = user_access_validator

    async def validate(self, user_id: ObjectId) -> User:
        """Checks if the current user can update user from request.

        Args:
            user_id (ObjectId): BSON object identifier of requested user.

        Returns:
            User: User object.

        Raises:
            HTTPException: If current user can't update requested one
            or user identifier is invalid.

        """

        user = await self.user_by_id_status_validator.validate(user_id=user_id)

        current_user = self.request.state.current_user

        if current_user.object.is_client is True:
            await self.user_access_validator.validate(user_id=user.id)

        elif user and user.is_client is True:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=HTTPErrorMessagesEnum.CLIENT_USER_ACCESS_DENIED,
            )

        return user


class UserPasswordUpdateValidator(BaseUserValidator):
    """User password update validator."""

    def __init__(
        self,
        request: Request,
        user_service: UserService = Depends(),
        user_access_validator: UserAccessValidator = Depends(),
    ) -> None:
        """Initializes user password update validator.

        Args:
            request (Request): Current request object.
            user_service (UserService): User service.
            user_access_validator (UserAccessValidator): User access validator.

        """

        super().__init__(request=request, user_service=user_service)

        self.user_access_validator = user_access_validator

    async def validate(self, user_id: ObjectId, old_password: str) -> None:
        """Checks if the current user can update own password.

        Args:
            user_id (ObjectId): BSON object identifier of requested user.
            old_password (str): Old password.

        Raises:
            HTTPException: If request and stored passwords doesn't match.

        """

        current_user = self.request.state.current_user

        # User can update only own password
        await self.user_access_validator.validate(user_id=user_id)

        if not Password.verify_password(
            plain_password=old_password,
            hashed_password=current_user.object.hashed_password,
        ):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=HTTPErrorMessagesEnum.PASSWORD_DOES_NOT_MATCH,
            )


class UserDeleteValidator(BaseUserValidator):
    """User delete validator."""

    def __init__(
        self,
        request: Request,
        user_service: UserService = Depends(),
        user_by_id_status_validator: UserByIdStatusValidator = Depends(),
        user_access_validator: UserAccessValidator = Depends(),
    ) -> None:
        """Initializes user delete validator.

        Args:
            request (Request): Current request object.
            user_service (UserService): User service.
            user_by_id_status_validator (UserByIdStatusValidator): User by id status
            validator.
            user_access_validator (UserAccessValidator): User access validator.

        """

        super().__init__(request=request, user_service=user_service)

        self.user_by_id_status_validator = user_by_id_status_validator

        self.user_access_validator = user_access_validator

    async def validate(self, user_id: ObjectId) -> User:
        """Checks if the current user can delete requested user.

        Args:
            user_id (ObjectId): BSON object identifier of requested user.

        Returns:
            User: User object.

        Raises:
            HTTPException: If current user can't delete requested one
            or user identifier is invalid.

        """

        user = await self.user_by_id_status_validator.validate(user_id=user_id)

        current_user = self.request.state.current_user

        if current_user.object.is_client is True:
            await self.user_access_validator.validate(user_id=user.id)

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
                detail=HTTPErrorMessagesEnum.ROLE_ACCESS_DENIED,
            )


class UserEmailVerifiedValidator(BaseUserValidator):
    """User email verified validator."""

    def __init__(
        self,
        request: Request,
        user_service: UserService = Depends(),
        user_by_username_status_validator: UserByUsernameStatusValidator = Depends(),
    ) -> None:
        """Initializes user email verified validator.

        Args:
            request (Request): Current request object.
            user_service (UserService): User service.
            user_by_username_status_validator (UserByUsernameStatusValidator): User by
            username status validator.

        """

        super().__init__(request=request, user_service=user_service)

        self.user_by_username_status_validator = user_by_username_status_validator

    async def validate(self, username: str) -> User:
        """Validates if user email is already verified.

        Args:
            username (str): Username of requested user.

        Returns:
            User: User object.

        Raises:
            HTTPException: If requested user email is verified.

        """

        user = await self.user_by_username_status_validator.validate(username=username)

        if user.email_verified is True:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=HTTPErrorMessagesEnum.EMAIL_IS_ALREADY_VERIFIED,
            )

        return user
