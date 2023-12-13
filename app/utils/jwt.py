"""Module that provides utility functions for creating JWT (JSON Web Token)."""

import arrow
from jose import JWTError, jwt
from pydantic import ValidationError

from app.api.v1.schemas.auth import TokenPayload, TokenUserData
from app.exceptions import ExpiredTokenError, InvalidTokenError
from app.settings import SETTINGS


class JWT:
    """Utility class for creating JWT tokens."""

    @staticmethod
    def _create_jwt_token(
        data: TokenUserData, secret_key: str, expires_delta: int
    ) -> str:
        """Create a JWT token with the provided data and expiration time.

        Args:
            data (dict): Data to include in the token payload.
            secret_key (str): Secret key for signing the token.
            expires_delta (int): Expiration time in minutes from the current time.

        Returns:
            JWT token.

        """
        expires_time = arrow.utcnow().shift(minutes=expires_delta)

        to_encode = data.model_dump()

        to_encode.update({"exp": expires_time.datetime})

        return jwt.encode(to_encode, secret_key, SETTINGS.AUTH_ALGORITHM)

    @staticmethod
    def create_access_token(
        data: TokenUserData, expires_delta: int | None = None
    ) -> str:
        """Create an access JWT token with the provided data and expiration time.

        Args:
            data (dict): Data to include in the token payload.
            expires_delta (int | None): Expiration time in minutes from the
                current time. If None, the default expiration time from settings
                will be used.

        Returns:
            JWT token.

        """
        return JWT._create_jwt_token(
            data,
            SETTINGS.AUTH_SECRET_KEY,
            expires_delta or SETTINGS.AUTH_ACCESS_TOKEN_EXPIRE_MINUTES,
        )

    @staticmethod
    def create_refresh_token(
        data: TokenUserData, expires_delta: int | None = None
    ) -> str:
        """Create a refresh JWT token with the provided data and expiration time.

        Args:
            data (dict): Data to include in the token payload.
            expires_delta (int | None): Expiration time in minutes from the
            current time. If None, the default expiration time from settings
            will be used.

        Returns:
            JWT token.

        """
        return JWT._create_jwt_token(
            data,
            SETTINGS.AUTH_REFRESH_SECRET_KEY,
            expires_delta or SETTINGS.AUTH_REFRESH_TOKEN_EXPIRE_MINUTES,
        )

    @staticmethod
    def parse_token(token: str) -> TokenPayload:
        """Parse and validate a JWT token.

        Args:
            token (str): The JWT token to parse.

        Returns:
            TokenPayload: The decoded token payload.

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

            token_data = TokenPayload(**payload)

            if arrow.get(token_data.exp) < arrow.utcnow():
                raise ExpiredTokenError

            return token_data

        except (JWTError, ValidationError):
            raise InvalidTokenError
