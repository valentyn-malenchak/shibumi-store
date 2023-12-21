"""
Module that provides utility functions for password hashing and verification
using the passlib library.
"""

from passlib.context import CryptContext


class Password:
    """Utility class for password hashing and verification."""

    _crypt_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hashes a password.

        Args:
            password (str): Plain password.

        Returns:
            str: Hashed password.

        """
        return Password._crypt_ctx.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verifies if a plain password matches its hashed counterpart.

        Args:
            plain_password (str): Plain password.
            hashed_password (str): Hashed password.

        Returns:
            bool: True if passwords match else False.

        """
        return Password._crypt_ctx.verify(plain_password, hashed_password)
