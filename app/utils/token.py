"""Contains verification token class."""

import hashlib
import secrets


class VerificationToken:
    """Verification token."""

    _TOKEN_BYTES = 32

    def __init__(self, value: str) -> None:
        """Initialize verification token.

        Args:
            value (str): Verification token value.

        """
        self.value = value

    @classmethod
    def generate(cls) -> "VerificationToken":
        """Generates a verification token."""
        return cls(value=secrets.token_urlsafe(cls._TOKEN_BYTES))

    def hash(self) -> str:
        """Hashes a verification token.

        Returns:
            str: Hashed token.

        """
        return hashlib.sha256(self.value.encode()).hexdigest()
