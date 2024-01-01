"""Module that provides application level constants."""

from enum import Enum


class EnvironmentsEnum(Enum):
    """Application environments enum."""

    DEV = "dev"
    PROD = "prod"


class HTTPErrorMessagesEnum(Enum):
    """Contains HTTP error messages."""

    INCORRECT_CREDENTIALS = "Incorrect username or password."
    EXPIRED_TOKEN = "Token is expired."
    INVALID_CREDENTIALS = "Invalid credentials."

    ENTITY_IS_NOT_FOUND = "{entity} is not found."
    ENTITY_FIELD_UNIQUENESS = "{entity} with such {field} is already exist."
