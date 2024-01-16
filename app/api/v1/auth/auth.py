"""
This module provides handling user authentication and authorization
using FastAPI security features and JWTs.
"""

import abc
from typing import List

from bson import ObjectId
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestFormStrict,
    SecurityScopes,
)

from app.api.v1.auth.jwt import JWT
from app.api.v1.auth.password import Password
from app.api.v1.constants import ScopesEnum
from app.api.v1.models.auth import TokenPayloadModel
from app.api.v1.models.user import CurrentUserModel
from app.api.v1.services.role_scopes import RoleScopesService
from app.api.v1.services.user import UserService
from app.constants import HTTPErrorMessagesEnum
from app.exceptions import ExpiredTokenError, InvalidTokenError


class Authentication:
    """Class for handling user authentication."""

    async def __call__(
        self,
        form_data: OAuth2PasswordRequestFormStrict = Depends(),
        user_service: UserService = Depends(),
        role_scope_service: RoleScopesService = Depends(),
    ) -> CurrentUserModel:
        """Authenticates a user using username and password.

        Args:
            form_data (OAuth2PasswordRequestForm): Form which contains
            username and password.
            role_scope_service (RoleScopesService): Roles-scopes service.

        Returns:
            CurrentUserModel: User object if token is valid and permitted scopes list.

        Raises:
            HTTPException: If authentication fails or not permitted scope is requested.

        """

        user = await user_service.get_by_username(username=form_data.username)

        if (
            user is None
            or user.deleted is True
            or not Password.verify_password(form_data.password, user.hashed_password)
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=HTTPErrorMessagesEnum.INCORRECT_CREDENTIALS.value,
            )

        permitted_scopes = await role_scope_service.get_scopes_by_roles(
            roles=user.roles
        )

        if form_data.scopes:
            # Verifies all requested in form data scopes are permitted
            BaseAuthorization.verify_scopes(
                source_scopes=permitted_scopes, required_scopes=form_data.scopes
            )

            scopes = form_data.scopes

        else:
            # If there are no requested scopes returns all permitted
            scopes = permitted_scopes

        return CurrentUserModel(object=user, scopes=scopes)


class BaseAuthorization(abc.ABC):
    """Base authorization class."""

    _oauth2 = OAuth2PasswordBearer(
        tokenUrl="/auth/tokens/",
        scheme_name="JWT",
        scopes={scope.name: scope.value for scope in ScopesEnum},
        auto_error=False,
    )

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
    def verify_scopes(source_scopes: List[str], required_scopes: List[str]) -> None:
        """Verifies all required scopes contain in source scopes.

        Args:
            source_scopes (List[str]): Source scopes.
            required_scopes (List[str]): Required scopes.

        """

        if not all(scope in source_scopes for scope in required_scopes):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=HTTPErrorMessagesEnum.PERMISSION_DENIED.value,
            )

    @staticmethod
    async def _authorize_user(
        token_data: TokenPayloadModel,
        security_scopes: SecurityScopes,
        request: Request,
        user_service: UserService,
    ) -> CurrentUserModel:
        """Authorizes the user.

        Args:
            token_data (TokenPayloadModel): JWT user data.
            security_scopes (SecurityScopes): Security scopes list.
            request (Request): Current request object.
            user_service (UserService): An instance of the User service.

        Returns:
            CurrentUserModel: User object if token is valid and permitted scopes list.

        """

        user = await user_service.get_by_id(id_=ObjectId(token_data.id))

        if user is None or user.deleted is True:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=HTTPErrorMessagesEnum.NOT_AUTHORIZED.value,
            )

        # Verifies all API security scopes are present in token
        BaseAuthorization.verify_scopes(
            source_scopes=token_data.scopes, required_scopes=security_scopes.scopes
        )

        request.state.current_user = CurrentUserModel(
            object=user, scopes=token_data.scopes
        )

        return request.state.current_user

    @abc.abstractmethod
    async def __call__(
        self,
        security_scopes: SecurityScopes,
        request: Request,
        token: str | None = Depends(_oauth2),
        user_service: UserService = Depends(),
    ) -> CurrentUserModel | None:
        """Authorizes the user using JWT.

        Args:
            security_scopes (SecurityScopes): Security scopes list.
            request (Request): Current request object.
            token (str | None): The JWT for authentication.
            user_service (UserService): An instance of the User service.

        Returns:
            CurrentUserModel | None: User object if token is valid and
            permitted scopes list.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.

        """
        raise NotImplementedError


class StrictAuthorization(BaseAuthorization):
    """Class for handling user strict authorization."""

    _uses_refresh_token: bool = False

    async def __call__(
        self,
        security_scopes: SecurityScopes,
        request: Request,
        token: str | None = Depends(BaseAuthorization._oauth2),
        user_service: UserService = Depends(),
    ) -> CurrentUserModel:
        """Authorizes the user using JWT strictly.

        Args:
            security_scopes (SecurityScopes): Security scopes list.
            request (Request): Current request object.
            token (str | None): The JWT for authentication.
            user_service (UserService): An instance of the User service.

        Returns:
            CurrentUserModel: User object if token is valid and permitted scopes list.

        """

        if token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=HTTPErrorMessagesEnum.NOT_AUTHORIZED.value,
            )

        token_data = self._parse_token(token=token, is_refresh=self._uses_refresh_token)

        return await self._authorize_user(
            token_data=token_data,
            security_scopes=security_scopes,
            request=request,
            user_service=user_service,
        )


class StrictRefreshTokenAuthorization(StrictAuthorization):
    """Class for handling user strict authorization with refresh token usage."""

    _uses_refresh_token: bool = True


class OptionalAuthorization(BaseAuthorization):
    """Class for handling user optional authorization."""

    async def __call__(
        self,
        security_scopes: SecurityScopes,
        request: Request,
        token: str | None = Depends(BaseAuthorization._oauth2),
        user_service: UserService = Depends(),
    ) -> CurrentUserModel | None:
        """Authorizes the user using JWT optionally.

        Args:
            security_scopes (SecurityScopes): Security scopes list.
            request (Request): Current request object.
            token (str | None): The JWT for authentication.
            user_service (UserService): An instance of the User service.

        Returns:
            CurrentUserModel | None: User object if token is valid and
            permitted scopes list.

        """

        if token is not None:
            token_data = self._parse_token(token=token)

            return await self._authorize_user(
                token_data=token_data,
                security_scopes=security_scopes,
                request=request,
                user_service=user_service,
            )

        return None
