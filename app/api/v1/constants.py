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

    HEALTH_GET_HEALTH = "Allows to check application health."

    AUTH_REFRESH_TOKEN = "Allows to refresh Access token using Refresh token."

    USERS_GET_ME = "Allows to get current user object."
    USERS_GET_USERS = "Allows to get users list."
    USERS_GET_USER = "Allow to get user."
    USERS_CREATE_USER = "Allows to create a new user."
    USERS_UPDATE_USER = "Allows to update user."
    USERS_UPDATE_USER_PASSWORD = "Allows to update user's password."
    USERS_DELETE_USER = "Allows to delete user."

    CATEGORIES_GET_CATEGORIES = "Allows to get categories list."
    CATEGORIES_GET_CATEGORY = "Allows to get category."
    CATEGORIES_GET_PARAMETERS_VALUES_BY_CATEGORY = (
        "Allows to get product parameters values by category."
    )

    PRODUCTS_CREATE_PRODUCT = "Allows to create a new product."
    PRODUCTS_GET_PRODUCTS = "Allows to get products list."
    PRODUCTS_GET_PRODUCT = "Allows to get product."


class RedisNamesEnum(Enum):
    """Redis names format enumerate."""

    EMAIL_VERIFICATION = "email_verification_{user_id}"
    RESET_PASSWORD = "reset_password_{user_id}"
    PRODUCT_PARAMETERS_LIST = "product_parameters"


class RedisNamesTTLEnum(Enum):
    """Redis names TTL enumerate."""

    EMAIL_VERIFICATION = 3600  # 1 hour
    RESET_PASSWORD = 3600  # 1 hour
    PRODUCT_PARAMETERS_LIST = 3600  # 1 hour


class EmailSubjectsEnum(Enum):
    """Email subjects enumerate."""

    EMAIL_VERIFICATION = "Shibumi Store - Email verification"
    RESET_PASSWORD = "Shibumi Store - Reset password"


class EmailTextEnum(Enum):
    """Email text enum."""

    EMAIL_VERIFICATION = "Email verification token: {token}"
    RESET_PASSWORD = "Reset password verification token: {token}"


class ProductParameterTypesEnum(Enum):
    """Product parameter types enumerate."""

    STR = str
    INT = int
    BOOL = bool
    LIST = list
