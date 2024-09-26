"""Contains auth domain dependencies."""

import abc

from bson import ObjectId
from fastapi import Depends, Request
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestFormStrict,
    SecurityScopes,
)

from app.api.v1.constants import ScopesEnum
from app.api.v1.models.auth import JWTPayload
from app.api.v1.models.user import CurrentUser
from app.api.v1.validators.auth import JWTValidator, ScopesByUserValidator
from app.api.v1.validators.user import (
    UserAuthenticationValidator,
    UserAuthorizationValidator,
    UserPasswordValidator,
)
from app.utils.metas import AbstractSingletonMeta, SingletonMeta


class AuthenticationDependency(metaclass=SingletonMeta):
    """Authentication dependency."""

    async def __call__(
        self,
        form_data: OAuth2PasswordRequestFormStrict = Depends(),
        scopes_by_user_validator: ScopesByUserValidator = Depends(),
        user_authentication_validator: UserAuthenticationValidator = Depends(),
        user_password_validator: UserPasswordValidator = Depends(),
    ) -> CurrentUser:
        """Authenticates a user using username and password.

        Args:
            form_data (OAuth2PasswordRequestForm): Form which contains
            username and password.
            scopes_by_user_validator (ScopesByUserValidator): Scopes by user validator.
            user_authentication_validator (UserAuthenticationValidator): User
            authentication validator.
            user_password_validator (UserPasswordValidator): User password validator.

        Returns:
            CurrentUser: Current user object and permitted scopes list.

        """

        user = await user_authentication_validator.validate(username=form_data.username)

        await user_password_validator.validate(user=user, password=form_data.password)

        return CurrentUser(
            object=user,
            scopes=await scopes_by_user_validator.validate(
                user=user, scopes=form_data.scopes
            ),
        )


class BaseAuthorizationDependency(abc.ABC, metaclass=AbstractSingletonMeta):
    """Base authorization dependency class."""

    _oauth2 = OAuth2PasswordBearer(
        tokenUrl="/auth/tokens/",
        scheme_name="JWT",
        scopes={scope.name: scope.value for scope in ScopesEnum},
        auto_error=False,
    )

    @staticmethod
    async def _validate_jwt(
        token: str | None, required_scopes: list[str], jwt_validator: JWTValidator
    ) -> JWTPayload:
        """Validates JWT.

        Args:
            token (str | None): The JWT for authentication.
            required_scopes (list[str]): Required scopes.
            jwt_validator (JWTValidator): JWT validator.

        Returns:
            JWTPayload: JWT payload.

        """
        return await jwt_validator.validate(
            token=token, required_scopes=required_scopes, is_refresh=False
        )

    @staticmethod
    async def _validate_user_by_token(
        request: Request,
        token_data: JWTPayload,
        user_authorization_validator: UserAuthorizationValidator,
    ) -> CurrentUser:
        """Validates user by JWT.

        Args:
            request (Request): Current request object.
            token_data (JWTPayload): JWT payload.
            user_authorization_validator (UserAuthorizationValidator): User
            authorization validator.

        Returns:
            CurrentUser: Current user object.

        """

        user = await user_authorization_validator.validate(
            user_id=ObjectId(token_data.id)
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
    ) -> CurrentUser | None:
        """Authorizes the user using JWT.

        Args:
            request (Request): Current request object.
            security_scopes (SecurityScopes): Security scopes list.
            token (str | None): The JWT for authentication.

        Returns:
            CurrentUser | None: Current user object or None.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.

        """
        raise NotImplementedError


class StrictAuthorizationDependency(BaseAuthorizationDependency):
    """Strict authorization dependency."""

    async def __call__(
        self,
        request: Request,
        security_scopes: SecurityScopes,
        token: str | None = Depends(BaseAuthorizationDependency._oauth2),
        jwt_validator: JWTValidator = Depends(),
        user_authorization_validator: UserAuthorizationValidator = Depends(),
    ) -> CurrentUser:
        """Authorizes the user using JWT strictly.

        Args:
            request (Request): Current request object.
            security_scopes (SecurityScopes): Security scopes list.
            token (str | None): The JWT for authentication.
            jwt_validator (JWTValidator): JWT validator.
            user_authorization_validator (UserAuthorizationValidator): User
            authorization validator.

        Returns:
            CurrentUser: Current user object.

        """

        token_data = await self._validate_jwt(
            token=token,
            required_scopes=security_scopes.scopes,
            jwt_validator=jwt_validator,
        )

        return await self._validate_user_by_token(
            request=request,
            token_data=token_data,
            user_authorization_validator=user_authorization_validator,
        )


class RefreshTokenAuthorizationDependency(StrictAuthorizationDependency):
    """Class for handling user strict authorization with refresh token usage."""

    @staticmethod
    async def _validate_jwt(
        token: str | None, required_scopes: list[str], jwt_validator: JWTValidator
    ) -> JWTPayload:
        """Validates JWT.

        Args:
            token (str | None): The JWT for authentication.
            required_scopes (list[str]): Required scopes.
            jwt_validator (JWTValidator): JWT validator.

        Returns:
            JWTPayload: JWT payload.

        """
        return await jwt_validator.validate(
            token=token, required_scopes=required_scopes, is_refresh=True
        )


class OptionalAuthorizationDependency(BaseAuthorizationDependency):
    """Class for handling user optional authorization."""

    async def __call__(
        self,
        request: Request,
        security_scopes: SecurityScopes,
        token: str | None = Depends(BaseAuthorizationDependency._oauth2),
        jwt_validator: JWTValidator = Depends(),
        user_authorization_validator: UserAuthorizationValidator = Depends(),
    ) -> CurrentUser | None:
        """Authorizes the user using JWT optionally.

        Args:
            request (Request): Current request object.
            security_scopes (SecurityScopes): Security scopes list.
            token (str | None): The JWT for authentication.
            jwt_validator (JWTValidator): JWT validator.
            user_authorization_validator (UserAuthorizationValidator): User
            authorization validator.

        Returns:
            CurrentUser | None: Current user object or None.

        """

        if token is None:
            return token

        token_data = await self._validate_jwt(
            token=token,
            required_scopes=security_scopes.scopes,
            jwt_validator=jwt_validator,
        )

        return await self._validate_user_by_token(
            request=request,
            token_data=token_data,
            user_authorization_validator=user_authorization_validator,
        )
