"""
This module provides handling user authentication and authorization
using FastAPI security features and JWTs.
"""

from typing import Annotated

from bson import ObjectId
from fastapi import Depends, HTTPException, status
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestFormStrict,
    SecurityScopes,
)

from app.api.v1.auth.jwt import JWT
from app.api.v1.auth.password import Password
from app.api.v1.constants import ScopesEnum
from app.api.v1.models.auth import TokenPayloadModel
from app.api.v1.models.users import User
from app.api.v1.services.users import UserService
from app.constants import HTTPErrorMessagesEnum
from app.exceptions import ExpiredTokenError, InvalidTokenError


class Authentication:
    """Class for handling user authentication."""

    async def __call__(
        self,
        form_data: Annotated[OAuth2PasswordRequestFormStrict, Depends()],
        user_service: UserService = Depends(),
    ) -> User:
        """Authenticates a user using username and password.

        Args:
            form_data (OAuth2PasswordRequestForm): Form which contains
            username and password.

        Returns:
            User: User object if authentication is successful.

        Raises:
            HTTPException: If authentication fails.

        """

        user = await user_service.get_item_by_username(username=form_data.username)

        if user is None or not Password.verify_password(
            form_data.password, user.hashed_password
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=HTTPErrorMessagesEnum.INCORRECT_CREDENTIALS.value,
            )

        return user


class StrictAuthorization:
    """Class for handling user strict authorization."""

    _oauth2 = OAuth2PasswordBearer(
        tokenUrl="/auth/tokens/",
        scheme_name="JWT",
        scopes={scope.name: scope.value for scope in ScopesEnum},
        auto_error=False,
    )

    def __init__(self, is_refresh_token: bool = False) -> None:
        """Initializes the Strict Authorization.

        Args:
            is_refresh_token (bool): Defines if refresh token used. Default to False.

        """

        self.is_refresh_token = is_refresh_token

    @staticmethod
    def _parse_token(token: str, is_refresh: bool = False) -> TokenPayloadModel:
        """Parses a JWT.

        Args:
            token (str): The JWT for authorization.
            is_refresh (bool): Defines if refresh token used. Default to False.

        Returns:
            TokenPayloadModel: JWT user data.

        Raises:
            HTTPException: If token is expired/invalid.

        """

        try:
            return JWT.decode_token(token, is_refresh=is_refresh)

        except ExpiredTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=HTTPErrorMessagesEnum.EXPIRED_TOKEN.value,
            )

        except InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=HTTPErrorMessagesEnum.INVALID_CREDENTIALS.value,
            )

    @staticmethod
    async def _authorize_user(
        token_data: TokenPayloadModel,
        security_scopes: SecurityScopes,
        user_service: UserService,
    ) -> User:
        """Authorizes the user.

        Args:
            token_data (TokenPayloadModel): JWT user data.
            security_scopes (SecurityScopes): Security scopes list.
            user_service (UserService): An instance of the User service.

        Returns:
            User: User object if token is valid.

        """

        user = await user_service.get_item_by_id(id_=ObjectId(token_data.id))

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=HTTPErrorMessagesEnum.NOT_AUTHORIZED.value,
            )

        # Verify user scopes
        if not any(scope in token_data.scopes for scope in security_scopes.scopes):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=HTTPErrorMessagesEnum.PERMISSION_DENIED.value,
            )

        return user

    async def __call__(
        self,
        security_scopes: SecurityScopes,
        token: str = Depends(_oauth2),
        user_service: UserService = Depends(),
    ) -> User:
        """Authorizes user using JWT strictly.

        Args:
            security_scopes (SecurityScopes): Security scopes list.
            token (str): The JWT for authentication.
            user_service (UserService): An instance of the User service.

        Returns:
            User: User object if token is valid.

        """

        if token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=HTTPErrorMessagesEnum.NOT_AUTHORIZED.value,
            )

        token_data = self._parse_token(token=token, is_refresh=self.is_refresh_token)

        return await self._authorize_user(
            token_data=token_data,
            security_scopes=security_scopes,
            user_service=user_service,
        )


class OptionalAuthorization(StrictAuthorization):
    """Class for handling user optional authorization."""

    async def __call__(
        self,
        security_scopes: SecurityScopes,
        token: str = Depends(StrictAuthorization._oauth2),
        user_service: UserService = Depends(),
    ) -> User:
        """Authorizes user using JWT optionally.

        Args:
            security_scopes (SecurityScopes): Security scopes list.
            token (str): The JWT for authentication.
            user_service (UserService): An instance of the User service.

        Returns:
            User | None: User object if there is token, and it is valid.

        """

        if token is not None:
            token_data = self._parse_token(
                token=token, is_refresh=self.is_refresh_token
            )

            return await self._authorize_user(
                token_data=token_data,
                security_scopes=security_scopes,
                user_service=user_service,
            )
