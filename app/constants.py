"""Module that provides application level constants."""

from enum import Enum

JTW_TYPE = "Bearer"


class HTTPErrorMessages(Enum):
    """Contains HTTP error messages."""

    INCORRECT_CREDENTIALS = "Incorrect username or password."
    EXPIRED_TOKEN = "Token is expired."
    INVALID_CREDENTIALS = "Invalid credentials."

    ENTITY_IS_NOT_FOUND = "{entity} is not found."
