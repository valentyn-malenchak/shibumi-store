"""Module that provides utility functions for manipulating JWT (JSON Web Token)."""

import arrow
from jose import ExpiredSignatureError, JWTError, jwt
from pydantic import ValidationError

from app.api.v1.models.auth import TokenPayloadModel, TokenUserModel
from app.exceptions import ExpiredTokenError, InvalidTokenError
from app.settings import SETTINGS


class JWT:
    """Utility class for manipulating JWTs."""

    _JTW_TYPE = "Bearer"

    @staticmethod
    def _encode_jwt(data: TokenUserModel, secret_key: str, expires_delta: int) -> str:
        """Encodes a JWT with the provided data and expiration time.

        Args:
            data (TokenUserModel): Data to include in the token payload.
            secret_key (str): Secret key for signing the token.
            expires_delta (int): Expiration time in minutes from the current time.

        Returns:
            str: JWT.

        """
        expires_time = arrow.utcnow().shift(minutes=expires_delta)

        to_encode = data.model_dump()

        to_encode.update({"exp": expires_time.datetime})

        return jwt.encode(to_encode, secret_key, SETTINGS.AUTH_ALGORITHM)

    @staticmethod
    def _encode_access_token(
        data: TokenUserModel, expires_delta: int | None = None
    ) -> str:
        """Encodes an access JWT with the provided data and expiration time.

        Args:
            data (TokenUserModel): Data to include in the token payload.
            expires_delta (int | None): Expiration time in minutes from the
                current time. If None, the default expiration time from settings
                will be used.

        Returns:
            str: JWT.

        """
        return JWT._encode_jwt(
            data,
            SETTINGS.AUTH_SECRET_KEY,
            expires_delta or SETTINGS.AUTH_ACCESS_TOKEN_EXPIRE_MINUTES,
        )

    @staticmethod
    def _encodes_refresh_token(
        data: TokenUserModel, expires_delta: int | None = None
    ) -> str:
        """Encodes a refresh JWT with the provided data and expiration time.

        Args:
            data (TokenUserModel): Data to include in the token payload.
            expires_delta (int | None): Expiration time in minutes from the
            current time. If None, the default expiration time from settings
            will be used.

        Returns:
            str: JWT.

        """
        return JWT._encode_jwt(
            data,
            SETTINGS.AUTH_REFRESH_SECRET_KEY,
            expires_delta or SETTINGS.AUTH_REFRESH_TOKEN_EXPIRE_MINUTES,
        )

    @staticmethod
    def encode_tokens(
        data: TokenUserModel,
        expires_delta: int | None = None,
        *,
        include_refresh: bool = True,
    ) -> dict[str, str]:
        """Encodes JWTs token with the provided data and expiration time.

        Args:
            data (TokenUserModel): Data to include in the token payload.
            expires_delta (int | None): Expiration time in minutes from the
            current time. If None, the default expiration time from settings
            will be used.
            include_refresh (bool): Defines if refresh token will be
            included to results.
            Defaults to True.

        Returns:
            dict[str, str]: JWT.

        """

        tokens = {
            "access_token": JWT._encode_access_token(data, expires_delta),
            "token_type": JWT._JTW_TYPE,
        }

        if include_refresh is True:
            tokens["refresh_token"] = JWT._encodes_refresh_token(data, expires_delta)

        return tokens

    @staticmethod
    def decode_token(token: str, is_refresh: bool = False) -> TokenPayloadModel:
        """Decodes and validates a JWT.

        Args:
            token (str): The JWT to decode.
            is_refresh (bool): Defines if token is refresh. Default to False.

        Returns:
            TokenPayloadModel: The decoded token payload.

        Raises:
            ExpiredTokenException: If the token is expired.
            InvalidTokenException: If the token is invalid or can't be decoded.

        """
        try:
            payload = jwt.decode(
                token,
                SETTINGS.AUTH_SECRET_KEY
                if is_refresh is False
                else SETTINGS.AUTH_REFRESH_SECRET_KEY,
                algorithms=[SETTINGS.AUTH_ALGORITHM],
            )

            return TokenPayloadModel(**payload)

        except ExpiredSignatureError:
            raise ExpiredTokenError

        except (JWTError, ValidationError):
            raise InvalidTokenError
