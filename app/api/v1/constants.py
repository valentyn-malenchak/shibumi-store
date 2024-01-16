"""Module that provides API v1 level constants."""

from enum import Enum


class RolesEnum(Enum):
    """User roles enumerate."""

    CUSTOMER = "Customer"
    SUPPORT = "Support"
    WAREHOUSE_STUFF = "Warehouse stuff"
    CONTENT_MANAGER = "Content manager"
    MARKETING_MANAGER = "Marketing manager"
    ADMIN = "Admin"


class ScopesEnum(Enum):
    """Scopes enumerate."""

    # Scope naming: {domain}_{action}_{entity}
    AUTH_REFRESH_TOKEN = "Allows to refresh Access token using Refresh token."
    HEALTH_GET_HEALTH = "Allows to check application health."
    USERS_GET_ME = "Allows to get current user object."
    USERS_GET_USERS = "Allows to get users list."
    USERS_GET_USER = "Allow to get user."
    USERS_CREATE_USER = "Allows to create a new user."
    USERS_UPDATE_USER = "Allows to update user."
    USERS_UPDATE_USER_PASSWORD = "Allows to update user's password."
    USERS_DELETE_USER = "Allows to delete user."


RESET_PASSWORD_TOKEN_BYTES = 32

RESET_PASSWORD_TOKEN_EXPIRATION_TIME = 3600  # 1 hour


class RedisNamesEnum(Enum):
    """Redis names format enumerate."""

    RESET_PASSWORD = "reset_password_{user_id}"


class EmailSubjectsEnum(Enum):
    """Email subjects enumerate."""

    RESET_PASSWORD = "FastAPI shop - Reset password"


class EmailTextEnum(Enum):
    """Email text enum."""

    RESET_PASSWORD = "Reset password verification token: {token}"
