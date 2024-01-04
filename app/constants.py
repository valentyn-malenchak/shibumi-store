"""Module that provides application level constants."""

from enum import Enum


class EnvironmentsEnum(Enum):
    """Application environments enumerate."""

    DEV = "dev"
    PROD = "prod"


class HTTPErrorMessagesEnum(Enum):
    """Contains HTTP error messages."""

    NOT_AUTHORIZED = "Not authorized."
    INCORRECT_CREDENTIALS = "Incorrect username or password."
    EXPIRED_TOKEN = "Token is expired."
    INVALID_CREDENTIALS = "Invalid credentials."
    PERMISSION_DENIED = "Permission denied."

    ENTITY_FIELD_UNIQUENESS = "{entity} with such {field} is already exist."
