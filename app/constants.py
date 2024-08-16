"""Module that provides application level constants."""

from enum import IntEnum, StrEnum


class AppConstants(IntEnum):
    """Application level constants enumerate."""

    PAGINATION_MAX_PAGE_SIZE = 100

    BACKGROUND_TASK_RETRY_ATTEMPTS = 3
    BACKGROUND_TASK_RETRY_WAIT = 5


class HTTPErrorMessagesEnum(StrEnum):
    """Contains HTTP error messages."""

    NOT_AUTHORIZED = "Not authorized."
    INCORRECT_CREDENTIALS = "Incorrect username or password."
    EXPIRED_TOKEN = "Token is expired."
    INVALID_CREDENTIALS = "Invalid credentials."
    PERMISSION_DENIED = "Permission denied."
    EMAIL_IS_NOT_VERIFIED = "Email is not verified."
    EMAIL_IS_ALREADY_VERIFIED = "Email is already verified."

    USER_ACCESS_DENIED = "Access denied to another user."
    ROLE_ACCESS_DENIED = "Access denied to use role."
    CLIENT_USER_ACCESS_DENIED = "Access denied to client user."
    CART_ACCESS_DENIED = "Access denied to another user's cart."

    ENTITY_IS_NOT_FOUND = "{entity} is not found."
    ENTITY_FIELD_UNIQUENESS = "{entity} with such '{field}' is already created."
    ENTITIES_ARE_NOT_RELATED = "{child_entity} is not related to the {parent_entity}."

    PASSWORD_DOES_NOT_MATCH = "The current password does not match."

    INVALID_RESET_PASSWORD_TOKEN = "Invalid or expired reset password token."
    INVALID_EMAIL_VERIFICATION_TOKEN = "Invalid or expired email verification token."

    LEAF_PRODUCT_CATEGORY_REQUIRED = (
        "Invalid category. Operation is allowed only for 'leaf' categories."
    )
    PRODUCT_ACCESS_DENIED = "Access denied to product."
    PRODUCTS_NOT_AVAILABLE_ACCESS_DENIED = "Access denied to not available products."

    MAXIMUM_PRODUCT_QUANTITY_AVAILABLE = (
        "Maximum available quantity for product is exceeded."
    )
    PRODUCT_IS_ALREADY_ADDED_TO_THE_CART = "Product is already added to the cart."
    PRODUCT_IS_NOT_ADDED_TO_THE_CART = "Product is not added to the cart."

    COMMENT_ACCESS_DENIED = "Access denied to comment."
    VOTE_ACCESS_DENIED = "Access denied to vote."
    INVALID_VOTE_VALUE = "Vote is already upvoted/downvoted."


class ValidationErrorMessagesEnum(StrEnum):
    """Contains validation error messages for Pydantic models."""

    INVALID_IDENTIFIER = "Invalid object identifier."
    REQUIRED_FIELD = "Field required."
    INVALID_FIELD_TYPE = "Field should be a valid {type_}."

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


class AppEventsEnum(StrEnum):
    """Application events enumerate."""

    STARTUP = "startup"
    SHUTDOWN = "shutdown"
