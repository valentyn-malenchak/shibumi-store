"""Contains auth domain validators."""

from typing import Any

from fastapi import Depends, HTTPException, Request, status

from app.api.v1.models.auth import JWTPayload
from app.api.v1.models.user import User
from app.api.v1.services.role import RoleService
from app.api.v1.services.user import UserService
from app.api.v1.validators import BaseValidator
from app.constants import HTTPErrorMessagesEnum
from app.exceptions import ExpiredTokenError, InvalidTokenError
from app.utils.jwt import JWT


class BaseAuthValidator(BaseValidator):
    """Base authentication/authorization validator."""

    async def validate(self, *args: Any) -> Any:
        """Validates data.

        Args:
            args (Any): Method arguments.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.

        """
        raise NotImplementedError


class ScopesRequiredValidator(BaseAuthValidator):
    """Authorization scopes required validator."""

    async def validate(
        self, source_scopes: list[str], required_scopes: list[str]
    ) -> None:
        """Validates all required scopes must contain in source scopes.

        Args:
            source_scopes (list[str]): Source scopes.
            required_scopes (list[str]): Required scopes.

        Raises:
            HTTPException: In case some required scopes are no included in
            source scopes.

        """

        if not all(scope in source_scopes for scope in required_scopes):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=HTTPErrorMessagesEnum.PERMISSION_DENIED,
            )


class ScopesByUserValidator(BaseAuthValidator):
    """Authorization scopes by user validator."""

    def __init__(
        self,
        request: Request,
        role_service: RoleService = Depends(),
        scopes_required_validator: ScopesRequiredValidator = Depends(),
    ) -> None:
        """Initializes scopes by user validator.

        Args:
            request (Request): Current request object.
            role_service (RoleService): Role service.
            scopes_required_validator (ScopesRequiredValidator): Scopes required
            validator.

        """

        super().__init__(request=request)

        self.role_service = role_service

        self.scopes_required_validator = scopes_required_validator

    async def validate(self, user: User, scopes: list[str] | None) -> list[str]:
        """Defines permitted scopes on authentication.

        Args:
            user (User): User object.
            scopes (list[str] | None): List of requested scopes.

        Returns:
            list[str]: List of permitted scopes.

        """

        permitted_scopes = await self.role_service.get_scopes_by_roles(roles=user.roles)

        if scopes:
            # Verifies all requested in form data scopes are permitted
            await self.scopes_required_validator.validate(
                source_scopes=permitted_scopes, required_scopes=scopes
            )

            return scopes

        # If there are no requested scopes returns all permitted
        return permitted_scopes


class JWTValidator(BaseAuthValidator):
    """JWT validator."""

    def __init__(
        self,
        request: Request,
        user_service: UserService = Depends(),
        scopes_required_validator: ScopesRequiredValidator = Depends(),
    ) -> None:
        """Initializes JWT validator.

        Args:
            request (Request): Current request object.
            user_service (UserService): User service.
            scopes_required_validator (ScopesRequiredValidator): Scopes required
            validator.

        """

        super().__init__(request=request)

        self.user_service = user_service

        self.scopes_required_validator = scopes_required_validator

    async def validate(
        self, token: str | None, required_scopes: list[str], is_refresh: bool
    ) -> JWTPayload:
        """Validates JWT.

        Args:
            token (str | None): The JWT for authentication or None.
            required_scopes (list[str]): Required scopes.
            is_refresh (bool): Defines if token is refresh or access.

        Returns:
            JWTPayload: JWT payload.

        Raises:
            HTTPException: In case token is missed/expired/invalid.

        """

        if token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=HTTPErrorMessagesEnum.NOT_AUTHORIZED,
            )

        try:
            token_data = JWT.decode_token(token, is_refresh=is_refresh)

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

        # Verifies all API security scopes are present in token
        await self.scopes_required_validator.validate(
            source_scopes=token_data.scopes, required_scopes=required_scopes
        )

        return token_data
