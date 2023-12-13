"""Module that contains users domain routers."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.v1.entities.auth import Authorization
from app.api.v1.schemas.users import User, UserResponseSchema

router = APIRouter(prefix="/users", tags=["users"])


# TODO: user shouldn't have an ability to login using refresh token
@router.get("/me/", response_model=UserResponseSchema)
async def get_users_me(
    current_user: Annotated[User, Depends(Authorization.authorize)],
) -> User:
    """API which return current user data.

    Args:
        current_user: User defined by Authorization token.

    Returns:
        Current user data.

    """
    return current_user
