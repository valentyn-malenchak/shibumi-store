"""Module that contains users domain routers."""


from fastapi import APIRouter, Depends, status

from app.api.v1.auth.auth import Authorization
from app.api.v1.models.users import CreateUserRequestModel, User, UserResponseModel
from app.api.v1.services.users import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me/", response_model=UserResponseModel, status_code=status.HTTP_200_OK)
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


@router.post("/", response_model=UserResponseModel, status_code=status.HTTP_201_CREATED)
async def create_users(
    user_data: CreateUserRequestModel,
    user_service: UserService = Depends(),
) -> User | None:
    """API which creates a new user.

    Args:
        user_data (CreateUserRequestModel): User registration data.
        user_service (UserService): User service.

    Returns:
        User | None: Created user data.

    """
    return await user_service.create_item(item=user_data)
