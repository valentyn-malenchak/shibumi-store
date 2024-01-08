"""Contains user domain validators."""


from typing import List

from bson import ObjectId
from fastapi import HTTPException, status

from app.api.v1.constants import RolesEnum
from app.api.v1.models.user import CurrentUserModel, User
from app.api.v1.services.user import UserService
from app.api.v1.validators import BaseValidator
from app.constants import HTTPErrorMessagesEnum


class UserSpecificValidator(BaseValidator):
    """User specific validator."""

    @classmethod
    def validate(cls, current_user: CurrentUserModel, user_id: str) -> None:
        """Checks if the current user is the same as requested.

        Args:
            current_user (CurrentUserModel): Current authorized
            user with permitted scopes.
            user_id (str): Identifier of requested user.

        Raises:
            HTTPException: If current and requested users are different.

        """

        if current_user.object.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=HTTPErrorMessagesEnum.USER_ACCESS_DENIED.value,
            )


class DeletedUserValidator(BaseValidator):
    """Deleted user validator"""

    @classmethod
    async def validate(
        cls, object_id: ObjectId, user_service: UserService
    ) -> User | None:
        """Validates requested user state.

        Args:
            object_id: BSON object identifier of requested user.
            user_service (UserService): User service.

        Returns:
            User: User object.

        Raises:
            HTTPException: If requested user is deleted.

        """

        user = await user_service.get_item_by_id(id_=object_id)

        if user and user.deleted is True:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=HTTPErrorMessagesEnum.ENTITY_IS_NOT_FOUND.value.format(
                    entity="User"
                ),
            )

        return user


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

        Raises:
            HTTPException: Not permitted roles are requested.

        """

        # Unauthenticated users or users with only 'Customer'
        # role can operate only with it
        if (current_user is None or current_user.object.is_client) and roles != [
            RolesEnum.CUSTOMER
        ]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=HTTPErrorMessagesEnum.ROLE_ACCESS_DENIED.value,
            )
