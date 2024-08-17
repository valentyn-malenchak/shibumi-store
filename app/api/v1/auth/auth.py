"""
This module provides handling user authentication and authorization
using FastAPI security features and JWTs.
"""

import abc

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
from app.api.v1.models.auth import JWTPayload
from app.api.v1.models.user import CurrentUser, User
from app.api.v1.services.role import RoleService
from app.api.v1.services.user import UserService
from app.constants import HTTPErrorMessagesEnum
from app.exceptions import EntityIsNotFoundError, ExpiredTokenError, InvalidTokenError


class Authentication:
    """Class for handling user authentication."""

    @staticmethod
    async def _verify_user(username: str, user_service: UserService) -> User:
        """Verifies user by username on authentication.

        Args:
            username (str): Username of requested user.
            user_service (UserService): An instance of the User service.

        Returns:
            User: User object.

        Raises:
            HTTPException: In case user by username is not found or user is deleted.

        """

        try:
            user = await user_service.get_by_username(username=username)

        except EntityIsNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=HTTPErrorMessagesEnum.INCORRECT_CREDENTIALS,
            )

        if user.deleted is True:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=HTTPErrorMessagesEnum.INCORRECT_CREDENTIALS,
            )

        return user

    @staticmethod
    async def _verify_password(
        user: User, password: str, user_service: UserService
    ) -> None:
        """Verifies user password on authentication.

        Args:
            user (User): User object.
            password (str): Requested user password.
            user_service (UserService): An instance of the User service.

        Raises:
            HTTPException: In case requested password is incorrect.

        """

        if not Password.verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=HTTPErrorMessagesEnum.INCORRECT_CREDENTIALS,
            )

        # update password hash parameters in database in case it is outdated
        if Password.verify_needs_rehash(user.hashed_password) is True:
            await user_service.update_password(id_=user.id, password=password)

    @staticmethod
    def verify_scopes(source_scopes: list[str], required_scopes: list[str]) -> None:
        """Verifies all required scopes must contain in source scopes.

        Args:
            source_scopes (list[str]): Source scopes.
            required_scopes (list[str]): Required scopes.

        Raises:
            HTTPException: in case some required scopes are no included in
            source scopes.

        """

        if not all(scope in source_scopes for scope in required_scopes):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=HTTPErrorMessagesEnum.PERMISSION_DENIED,
            )

    @staticmethod
    async def _get_scopes(
        user: User, scopes: list[str] | None, role_service: RoleService
    ) -> list[str]:
        """Defines permitted scopes on authentication.

        Args:
            user (User): User object.
            scopes (list[str] | None): List of requested scopes.
            role_service (RoleService): An instance of the Role service.

        Returns:
            list[str]: List of permitted scopes.

        """

        permitted_scopes = await role_service.get_scopes_by_roles(roles=user.roles)

        if scopes:
            # Verifies all requested in form data scopes are permitted
            Authentication.verify_scopes(
                source_scopes=permitted_scopes, required_scopes=scopes
            )

            return scopes

        # If there are no requested scopes returns all permitted
        return permitted_scopes

    async def __call__(
        self,
        form_data: OAuth2PasswordRequestFormStrict = Depends(),
        role_service: RoleService = Depends(),
        user_service: UserService = Depends(),
    ) -> CurrentUser:
        """Authenticates a user using username and password.

        Args:
            form_data (OAuth2PasswordRequestForm): Form which contains
            username and password.
            role_service (RoleService): An instance of the Role service.
            user_service (UserService): An instance of the User service.

        Returns:
            CurrentUser: Current user object and permitted scopes list.

        """

        user = await self._verify_user(
            username=form_data.username, user_service=user_service
        )

        await self._verify_password(
            user=user, password=form_data.password, user_service=user_service
        )

        return CurrentUser(
            object=user,
            scopes=await self._get_scopes(
                user=user, scopes=form_data.scopes, role_service=role_service
            ),
        )


class BaseAuthorization(abc.ABC):
    """Base authorization class."""

    _oauth2 = OAuth2PasswordBearer(
        tokenUrl="/auth/tokens/",
        scheme_name="JWT",
        scopes={scope.name: scope.value for scope in ScopesEnum},
        auto_error=False,
    )

    @staticmethod
    async def _verify_user(id_: ObjectId, user_service: UserService) -> User:
        """Verifies user by identifier on authorization.

        Args:
            id_ (ObjectId): BSON object identifier of requested user.
            user_service (UserService): An instance of the User service.

        Returns:
            User: User object.

        Raises:
            HTTPException: In case user by username is not found, user is deleted
            or user's email is not verified.

        """

        try:
            user = await user_service.get_by_id(id_=id_)

        except EntityIsNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=HTTPErrorMessagesEnum.NOT_AUTHORIZED,
            )

        if user.deleted is True:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=HTTPErrorMessagesEnum.NOT_AUTHORIZED,
            )

        if user.email_verified is False:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=HTTPErrorMessagesEnum.EMAIL_IS_NOT_VERIFIED,
            )

        return user

    @staticmethod
    def _decode_jwt(token: str) -> JWTPayload:
        """Decodes JWT.

        Args:
            token (str): The JWT for authorization.

        Returns:
            JWTPayload: JWT payload.

        """
        return JWT.decode_token(token, is_refresh=False)

    def _parse_token(self, token: str) -> JWTPayload:
        """Parses a JWT.

        Args:
            token (str): The JWT for authorization.

        Returns:
            JWTPayload: JWT payload.

        Raises:
            HTTPException: In case token is expired/invalid.

        """

        try:
            return self._decode_jwt(token=token)

        except ExpiredTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=HTTPErrorMessagesEnum.EXPIRED_TOKEN,
            )

        except InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=HTTPErrorMessagesEnum.INVALID_CREDENTIALS,
            )

    async def _authorize_user(
        self,
        request: Request,
        token: str,
        security_scopes: SecurityScopes,
        user_service: UserService,
    ) -> CurrentUser:
        """Authorizes the user.

        Args:
            request (Request): Current request object.
            token (str): The JWT for authentication.
            security_scopes (SecurityScopes): Security scopes list.
            user_service (UserService): An instance of the User service.

        Returns:
            CurrentUser: Current user object if token is valid and permitted
            scopes list.

        """

        token_data = self._parse_token(token=token)

        user = await BaseAuthorization._verify_user(
            id_=ObjectId(token_data.id), user_service=user_service
        )

        # Verifies all API security scopes are present in token
        Authentication.verify_scopes(
            source_scopes=token_data.scopes, required_scopes=security_scopes.scopes
        )

        # Stores current user in current request object
        request.state.current_user = CurrentUser(object=user, scopes=token_data.scopes)

        return request.state.current_user

    @abc.abstractmethod
    async def __call__(
        self,
        request: Request,
        security_scopes: SecurityScopes,
        token: str | None = Depends(_oauth2),
        user_service: UserService = Depends(),
    ) -> CurrentUser | None:
        """Authorizes the user using JWT.

        Args:
            request (Request): Current request object.
            security_scopes (SecurityScopes): Security scopes list.
            token (str | None): The JWT for authentication.
            user_service (UserService): An instance of the User service.

        Returns:
            CurrentUser | None: Current user object if token is valid and
            permitted scopes list.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.

        """
        raise NotImplementedError


class StrictAuthorization(BaseAuthorization):
    """Class for handling user strict authorization."""

    async def __call__(
        self,
        request: Request,
        security_scopes: SecurityScopes,
        token: str | None = Depends(BaseAuthorization._oauth2),
        user_service: UserService = Depends(),
    ) -> CurrentUser:
        """Authorizes the user using JWT strictly.

        Args:
            request (Request): Current request object.
            security_scopes (SecurityScopes): Security scopes list.
            token (str | None): The JWT for authentication.
            user_service (UserService): An instance of the User service.

        Returns:
            CurrentUser: Current user object if token is valid and permitted
            scopes list.

        Raises:
            HTTPException: In case JWT is not provided.

        """

        if token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=HTTPErrorMessagesEnum.NOT_AUTHORIZED,
            )

        return await self._authorize_user(
            request=request,
            security_scopes=security_scopes,
            token=token,
            user_service=user_service,
        )


class RefreshTokenAuthorization(StrictAuthorization):
    """Class for handling user strict authorization with refresh token usage."""

    @staticmethod
    def _decode_jwt(token: str) -> JWTPayload:
        """Decodes JWT.

        Args:
            token (str): The JWT for authorization.

        Returns:
            JWTPayload: JWT payload.

        """
        return JWT.decode_token(token, is_refresh=True)


class OptionalAuthorization(BaseAuthorization):
    """Class for handling user optional authorization."""

    async def __call__(
        self,
        request: Request,
        security_scopes: SecurityScopes,
        token: str | None = Depends(BaseAuthorization._oauth2),
        user_service: UserService = Depends(),
    ) -> CurrentUser | None:
        """Authorizes the user using JWT optionally.

        Args:
            request (Request): Current request object.
            security_scopes (SecurityScopes): Security scopes list.
            token (str | None): The JWT for authentication.
            user_service (UserService): An instance of the User service.

        Returns:
            CurrentUser | None: Current user object if token is valid and
            permitted scopes list.

        """

        if token is not None:
            return await self._authorize_user(
                request=request,
                security_scopes=security_scopes,
                token=token,
                user_service=user_service,
            )

        return None
