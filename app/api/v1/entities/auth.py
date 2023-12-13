"""
This module provides handling user authentication and authorization
using FastAPI security features and JWT tokens.
"""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.api.v1.entities import BaseEntity
from app.api.v1.entities.users import UserEntity
from app.api.v1.schemas.users import User
from app.constants import HTTPErrorMessages
from app.exceptions import ExpiredTokenError, InvalidTokenError
from app.utils.jwt import JWT
from app.utils.password import Password


class Authentication(BaseEntity):
    """Authentication class for handling user authentication."""

    @classmethod
    async def authenticate(cls, username: str, password: str) -> User:
        """Authenticate a user using username and password.

        Args:
            username (str): The username of the user.
            password (str): The password of the user.

        Returns:
            User data if authentication is successful.

        Raises:
            HTTPException: If authentication fails.

        """

        user = await UserEntity().get_user_by_username(username=username)

        if user is None or not Password.verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=HTTPErrorMessages.INCORRECT_CREDENTIALS.value,
            )

        return user


class Authorization(BaseEntity):
    """Authorization class for handling user authorization."""

    _oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/tokens/", scheme_name="JWT")

    @classmethod
    async def authorize(cls, token: Annotated[str, Depends(_oauth2)]) -> User:
        """Get the current user based on the provided token.

        Args:
            token (str): The JWT token for authentication.

        Returns:
            User data if token is valid.

        Raises:
            HTTPException: If token is expired or invalid.

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

        user = await UserEntity().get_user_by_username(username=token_data.username)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=HTTPErrorMessages.ENTITY_IS_NOT_FOUND.value.format(
                    entity="User"
                ),
            )

        return user
