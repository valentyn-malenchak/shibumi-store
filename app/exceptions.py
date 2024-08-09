"""Module that provides custom application exceptions."""


class ApplicationError(Exception):
    """Custom application exception."""


class ExpiredTokenError(ApplicationError):
    """Expired JWT exception."""


class InvalidTokenError(ApplicationError):
    """Invalid JWT exception."""


class EntityIsNotFoundError(ApplicationError):
    """Entity is not found error."""


class EntityDuplicateKeyError(ApplicationError):
    """Entity duplicate key error."""
