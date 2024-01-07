"""Contains user domain dependencies."""


from bson import ObjectId
from fastapi import HTTPException, Request, status

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

        if not ObjectId.is_valid(user_id):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=HTTPErrorMessagesEnum.INVALID_IDENTIFIER.value,
            )

        current_user = request.state.current_user

        if current_user.object.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=HTTPErrorMessagesEnum.PERMISSION_DENIED.value,
            )

        return user_id
