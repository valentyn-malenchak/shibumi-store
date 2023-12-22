"""Module that contains users domain routers."""


from fastapi import APIRouter, Depends

from app.api.v1.auth.auth import Authorization
from app.api.v1.models.users import User, UserResponseModel

router = APIRouter(prefix="/users", tags=["users"])


# TODO: user shouldn't have an ability to login using refresh token
@router.get("/me/", response_model=UserResponseModel)
async def get_users_me(
    token: str = Depends(Authorization.oauth2),
    authorization: Authorization = Depends(),
) -> User:
    """API which returns current user data.

    Args:
        token (str): User's Authorization Bearer token.
        authorization (Authorization): Authorization handler.

    Returns:
        User: Current user data.

    """
    return await authorization.authorize(token)
