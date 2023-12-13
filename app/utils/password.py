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
        """Hash a password and return the hash."""
        return Password._crypt_ctx.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify if a plain password matches its hashed counterpart."""
        return Password._crypt_ctx.verify(plain_password, hashed_password)
