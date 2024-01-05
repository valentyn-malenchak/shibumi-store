"""Contains user domain dependencies."""

from fastapi import HTTPException, Security, status

from app.api.v1.auth.auth import StrictAuthorization
from app.api.v1.constants import ScopesEnum
from app.api.v1.models.users import User
from app.constants import HTTPErrorMessagesEnum


class UserUpdateDependency:
    """User update dependency."""

    async def __call__(
        self,
        user_id: str,
        current_user: User = Security(
            StrictAuthorization(), scopes=[ScopesEnum.USERS_UPDATE_USERS.name]
        ),
    ) -> User | None:
        """Checks if the current user can update information.

        Args:
            user_id (str): Identifier of user that should be updated.
            current_user (User): Current user object.

        Returns:
            User: Current user object.

        Raises:
            HTTPException: If current and requested users are different.

        """

        if current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=HTTPErrorMessagesEnum.PERMISSION_DENIED.value,
            )

        return current_user
