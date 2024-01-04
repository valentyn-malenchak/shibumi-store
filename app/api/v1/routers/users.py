"""Module that contains users domain routers."""


from fastapi import APIRouter, Depends, Security, status

from app.api.v1.auth.auth import OptionalAuthorization, StrictAuthorization
from app.api.v1.constants import ScopesEnum
from app.api.v1.models.users import CreateUserRequestModel, User, UserResponseModel
from app.api.v1.services.users import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me/", response_model=UserResponseModel, status_code=status.HTTP_200_OK)
async def get_users_me(
    user: User = Security(StrictAuthorization(), scopes=[ScopesEnum.USERS_GET_ME.name]),
) -> User:
    """API which returns current user object.

    Args:
        user (User): Current User object.

    Returns:
        User: Current user object.

    """
    return user


@router.post("/", response_model=UserResponseModel, status_code=status.HTTP_201_CREATED)
async def create_users(
    user_data: CreateUserRequestModel,
    _: User | None = Security(
        OptionalAuthorization(), scopes=[ScopesEnum.USERS_CREATE_USERS.name]
    ),
    user_service: UserService = Depends(),
) -> User | None:
    """API which creates a new user.

    Args:
        user_data (CreateUserRequestModel): User registration data.
        _: Current user object.
        user_service (UserService): User service.

    Returns:
        User | None: Created user object.

    """
    return await user_service.create_item(item=user_data)
