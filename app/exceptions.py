"""Module that provides custom application exceptions."""


class AppExceptionError(Exception):
    """Custom application exception."""


class ExpiredTokenError(AppExceptionError):
    """Expired JWT exception."""


class InvalidTokenError(AppExceptionError):
    """Invalid JWT exception."""
