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

    AUTH_REFRESH_TOKEN = "Allows to refresh Access token using Refresh token."
    HEALTH_GET_HEALTH = "Allows to check application health."
    USERS_GET_ME = "Allow to get current user object."
    USERS_CREATE_USERS = "Allows to create a new user."
    USERS_UPDATE_USERS = "Allows to update user."
