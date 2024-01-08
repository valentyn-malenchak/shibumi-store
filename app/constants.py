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
    INVALID_IDENTIFIER = "Invalid object identifier."

    USER_ACCESS_DENIED = "Access denied to another user."
    ROLE_ACCESS_DENIED = "Access denied to use role."

    ENTITY_FIELD_UNIQUENESS = "{entity} with such {field} is already exist."


# Password policies
PASSWORD_MIN_CHARACTERS_POLICY = 8

# Username policies
USERNAME_MIN_CHARACTERS_POLICY = 8
USERNAME_MAX_CHARACTERS_POLICY = 30
USERNAME_ALLOWED_SPECIAL_CHARACTER = "_-."


class ValidationErrorMessagesEnum(Enum):
    """Contains validation error messages for Pydantic models."""

    # Password policies
    PASSWORD_MIN_LENGTH = "Password must contain at least eight characters."
    PASSWORD_WITHOUT_DIGIT = "Password must contain at least one digit."
    PASSWORD_WITHOUT_LOWERCASE_LETTER = (
        "Password must contain at least one lowercase letter."
    )
    PASSWORD_WITHOUT_UPPERCASE_LETTER = (
        "Password must contain at least one uppercase letter."
    )
    PASSWORD_WITHOUT_SPECIAL_CHARACTER = (
        "Password must contain at least one special character."
    )

    # Username policies
    USERNAME_MIN_LENGTH = "Username must contain at least eight characters."
    USERNAME_MAX_LENGTH = "Username must contain at most thirty characters."
    USERNAME_NOT_ALLOWED_CHARACTERS = (
        "Username must contain only alphanumeric characters, "
        "hyphen, underscore, or dot."
    )
