"""Module that contains MongoDB constants."""

from enum import StrEnum


class MongoCollectionsEnum(StrEnum):
    """MongoDB's collections enumeration."""

    USERS = "users"
    ROLES = "roles"
    CATEGORIES = "categories"
    PRODUCTS = "products"
    PARAMETERS = "parameters"
    CATEGORY_PARAMETERS = "category_parameters"
