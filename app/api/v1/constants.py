"""Module that provides API v1 level constants."""

from enum import Enum, IntEnum, StrEnum, auto


class RolesEnum(StrEnum):
    """User roles enumerate."""

    CUSTOMER = auto()
    SUPPORT = auto()
    WAREHOUSE_STUFF = auto()
    CONTENT_MANAGER = auto()
    MARKETING_MANAGER = auto()
    ADMIN = auto()


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

    ROLES_GET_ROLES = "Allows to get roles list."

    CATEGORIES_GET_CATEGORIES = "Allows to get categories list."
    CATEGORIES_GET_CATEGORY = "Allows to get category."
    CATEGORIES_GET_CATEGORY_PARAMETERS = "Allows to get calculated category parameters."

    PRODUCTS_GET_PRODUCTS = "Allows to get products list."
    PRODUCTS_GET_PRODUCT = "Allows to get product."
    PRODUCTS_CREATE_PRODUCT = "Allows to create a new product."
    PRODUCTS_UPDATE_PRODUCT = "Allows to update product."

    CARTS_GET_CART = "Allows to get user's cart."
    CARTS_ADD_PRODUCT = "Allows to add product to the cart."
    CARTS_UPDATE_PRODUCT = "Allows to update product in the cart."
    CARTS_DELETE_PRODUCT = "Allows to delete product from the cart."

    THREADS_GET_THREAD = "Allows to get thread."
    THREADS_GET_COMMENT = "Allows to get thread comment."
    THREADS_CREATE_COMMENT = "Allows to create a thread comment."
    THREADS_UPDATE_COMMENT = "Allows to update a thread comment."
    THREADS_GET_VOTE = "Allows to get thread comment vote."
    THREADS_CREATE_VOTE = "Allows to create a thread comment vote."
    THREADS_UPDATE_VOTE = "Allows to update a thread comment vote."


class RedisNamesEnum(StrEnum):
    """Redis names format enumerate."""

    EMAIL_VERIFICATION = "email_verification_{user_id}"
    RESET_PASSWORD = "reset_password_{user_id}"
    PRODUCT_PARAMETERS_LIST = "product_parameters"
    ROLES_LIST = "roles"


class RedisNamesTTLEnum(IntEnum):
    """Redis names TTL enumerate."""

    EMAIL_VERIFICATION = 3600  # 1 hour
    RESET_PASSWORD = 3600  # 1 hour
    PRODUCT_PARAMETERS_LIST = 3600  # 1 hour
    ROLES_LIST = 3600  # 1 hour


class EmailSubjectsEnum(StrEnum):
    """Email subjects enumerate."""

    EMAIL_VERIFICATION = "Shibumi Store - Email verification"
    RESET_PASSWORD = "Shibumi Store - Reset password"


class EmailTextEnum(StrEnum):
    """Email text enum."""

    EMAIL_VERIFICATION = "Email verification token: {token}"
    RESET_PASSWORD = "Reset password verification token: {token}"


class ProductParameterTypesEnum(Enum):
    """Product parameter types enumerate."""

    STR = str
    INT = int
    BOOL = bool
    LIST = list
