"""Module that contains SendGrid constants."""

from enum import StrEnum


class EmailSubjectsEnum(StrEnum):
    """Email subjects enumerate."""

    EMAIL_VERIFICATION = "Shibumi Store - Email verification"
    RESET_PASSWORD = "Shibumi Store - Reset password"


class EmailTextEnum(StrEnum):
    """Email text enumerate."""

    EMAIL_VERIFICATION = "Email verification token: {token}"
    RESET_PASSWORD = "Reset password verification token: {token}"
