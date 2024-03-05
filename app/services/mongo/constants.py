"""Module that contains MongoDB constants."""

from enum import StrEnum


class MongoCollectionsEnum(StrEnum):
    """MongoDB's collections enumeration."""

    USERS = "users"
    ROLES_SCOPES = "roles_scopes"
    CATEGORIES = "categories"
    PRODUCTS = "products"
    PARAMETERS = "parameters"
    PARAMETERS_VALUES = "parameters_values"
