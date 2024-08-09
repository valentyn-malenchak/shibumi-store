"""Module that contains MongoDB constants."""

from enum import IntEnum, StrEnum, auto


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
    COMMENTS = auto()
    VOTES = auto()


class SortingTypesEnum(StrEnum):
    """Sorting types enumerate."""

    ASC = auto()
    DESC = auto()


class SortingValuesEnum(IntEnum):
    """Sorting values enumerate."""

    ASC = 1
    DESC = -1


class ProjectionValuesEnum(IntEnum):
    """Projection values enumerate."""

    INCLUDE = 1
    EXCLUDE = 0
