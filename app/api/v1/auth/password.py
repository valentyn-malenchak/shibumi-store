"""
Module that provides utility functions for password hashing and verification
using the argon2 library.
"""

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


class Password:
    """Utility class for password hashing and verification."""

    _hasher = PasswordHasher()

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hashes a password.

        Args:
            password (str): Plain password.

        Returns:
            str: Hashed password.

        """
        return Password._hasher.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verifies if a plain password matches its hashed counterpart.

        Args:
            plain_password (str): Plain password.
            hashed_password (str): Hashed password.

        Returns:
            bool: True if passwords match else False.

        """
        try:
            return Password._hasher.verify(hashed_password, plain_password)
        except VerifyMismatchError:
            return False

    @staticmethod
    def check_needs_rehash(hashed_password: str) -> bool:
        """Verifies if parameters of hashed password are outdated.

        Args:
            hashed_password (str): Hashed password.

        Returns:
            bool: True if hash parameters are outdated else False.

        """
        return Password._hasher.check_needs_rehash(hashed_password)
