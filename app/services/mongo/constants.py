"""Module that contains MongoDB constants."""

from enum import Enum


class MongoCollectionsEnum(Enum):
    """MongoDB's collections enumeration."""

    USERS = "users"
    ROLES_SCOPES = "roles_scopes"
    CATEGORIES = "categories"
    PRODUCTS = "products"
    PARAMETERS = "parameters"
