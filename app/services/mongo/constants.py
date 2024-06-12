"""Module that contains MongoDB constants."""

from enum import StrEnum, auto


class MongoCollectionsEnum(StrEnum):
    """MongoDB's collections enumeration."""

    USERS = auto()
    ROLES = auto()
    CATEGORIES = auto()
    PRODUCTS = auto()
    PARAMETERS = auto()
    CATEGORY_PARAMETERS = auto()
    CARTS = auto()
    THREADS = auto()
