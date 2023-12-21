"""
This module provides handling user authentication and authorization
using FastAPI security features and JWT tokens.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.api.v1.auth.jwt import JWT
from app.api.v1.auth.password import Password
from app.api.v1.models.users import User
from app.api.v1.services.users import UserService
from app.constants import HTTPErrorMessages
from app.exceptions import ExpiredTokenError, InvalidTokenError


class Authentication:
    """Class for handling user authentication."""

    def __init__(self, user_service: UserService = Depends()) -> None:
        """Initializes the Authentication.

        Args:
            user_service (UserService): An instance of the User service.

        """
        self.user_service = user_service

    async def authenticate(self, username: str, password: str) -> User:
        """Authenticates a user using username and password.

        Args:
            username (str): The username of the user.
            password (str): The password of the user.

        Returns:
            User: User data if authentication is successful.

        Raises:
            HTTPException: If authentication fails.

        """

        user = await self.user_service.get_item_by_username(username=username)

        if user is None or not Password.verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=HTTPErrorMessages.INCORRECT_CREDENTIALS.value,
            )

        return user


class Authorization:
    """Class for handling user authorization."""

    oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/tokens/", scheme_name="JWT")

    def __init__(self, user_service: UserService = Depends()) -> None:
        """Initializes the Authorization.

        Args:
            user_service (UserService): An instance of the User service.

        """

        self.user_service = user_service

    async def authorize(self, token: str) -> User:
        """Gets the current user based on the provided token.

        Args:
            token (str): The JWT token for authentication.

        Returns:
            User: User data if token is valid.

        Raises:
            HTTPException: If token is expired/invalid or user does not exist.

        """
        try:
            token_data = JWT.parse_token(token)

        except ExpiredTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=HTTPErrorMessages.EXPIRED_TOKEN.value,
            )

        except InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=HTTPErrorMessages.INVALID_CREDENTIALS.value,
            )

        user = await self.user_service.get_item_by_username(
            username=token_data.username
        )

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=HTTPErrorMessages.ENTITY_IS_NOT_FOUND.value.format(
                    entity="User"
                ),
            )

        return user
