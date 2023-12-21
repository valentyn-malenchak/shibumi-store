"""Module that provides utility functions for creating JWT (JSON Web Token)."""

from typing import Dict

import arrow
from jose import ExpiredSignatureError, JWTError, jwt
from pydantic import ValidationError

from app.api.v1.models.auth import TokenPayloadModel, TokenUserModel
from app.exceptions import ExpiredTokenError, InvalidTokenError
from app.settings import SETTINGS


class JWT:
    """Utility class for creating JWT tokens."""

    _JTW_TYPE = "Bearer"

    @staticmethod
    def _create_jwt_token(
        data: TokenUserModel, secret_key: str, expires_delta: int
    ) -> str:
        """Creates a JWT token with the provided data and expiration time.

        Args:
            data (TokenUserModel): Data to include in the token payload.
            secret_key (str): Secret key for signing the token.
            expires_delta (int): Expiration time in minutes from the current time.

        Returns:
            str: JWT token.

        """
        expires_time = arrow.utcnow().shift(minutes=expires_delta)

        to_encode = data.model_dump()

        to_encode.update({"exp": expires_time.datetime})

        return jwt.encode(to_encode, secret_key, SETTINGS.AUTH_ALGORITHM)

    @staticmethod
    def _create_access_token(
        data: TokenUserModel, expires_delta: int | None = None
    ) -> str:
        """Creates an access JWT token with the provided data and expiration time.

        Args:
            data (TokenUserModel): Data to include in the token payload.
            expires_delta (int | None): Expiration time in minutes from the
                current time. If None, the default expiration time from settings
                will be used.

        Returns:
            str: JWT token.

        """
        return JWT._create_jwt_token(
            data,
            SETTINGS.AUTH_SECRET_KEY,
            expires_delta or SETTINGS.AUTH_ACCESS_TOKEN_EXPIRE_MINUTES,
        )

    @staticmethod
    def _create_refresh_token(
        data: TokenUserModel, expires_delta: int | None = None
    ) -> str:
        """Creates a refresh JWT token with the provided data and expiration time.

        Args:
            data (TokenUserModel): Data to include in the token payload.
            expires_delta (int | None): Expiration time in minutes from the
            current time. If None, the default expiration time from settings
            will be used.

        Returns:
            str: JWT token.

        """
        return JWT._create_jwt_token(
            data,
            SETTINGS.AUTH_REFRESH_SECRET_KEY,
            expires_delta or SETTINGS.AUTH_REFRESH_TOKEN_EXPIRE_MINUTES,
        )

    @staticmethod
    def create_tokens(
        data: TokenUserModel,
        expires_delta: int | None = None,
        *,
        include_refresh: bool = True,
    ) -> Dict[str, str]:
        """Creates JWT tokens token with the provided data and expiration time.

        Args:
            data (TokenUserModel): Data to include in the token payload.
            expires_delta (int | None): Expiration time in minutes from the
            current time. If None, the default expiration time from settings
            will be used.
            include_refresh (bool): Defines if refresh token will be
            included to results.
            Defaults to True.

        Returns:
            Dict[str, str]: JWT token.

        """

        tokens = {
            "access_token": JWT._create_access_token(data, expires_delta),
            "token_type": JWT._JTW_TYPE,
        }

        if include_refresh is True:
            tokens["refresh_token"] = JWT._create_refresh_token(data, expires_delta)

        return tokens

    @staticmethod
    def parse_token(token: str) -> TokenPayloadModel:
        """Parses and validates a JWT token.

        Args:
            token (str): The JWT token to parse.

        Returns:
            TokenPayloadModel: The decoded token payload.

        Raises:
            ExpiredTokenException: If the token is expired.
            InvalidTokenException: If the token is invalid or can't be decoded.

        """
        try:
            payload = jwt.decode(
                token,
                SETTINGS.AUTH_SECRET_KEY,
                algorithms=[SETTINGS.AUTH_ALGORITHM],
            )

            return TokenPayloadModel(**payload)

        except ExpiredSignatureError:
            raise ExpiredTokenError

        except (JWTError, ValidationError):
            raise InvalidTokenError
