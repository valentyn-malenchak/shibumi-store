"""Module that contains Redis constants."""

from enum import IntEnum, StrEnum


class RedisNamesEnum(StrEnum):
    """Redis names format enumerate."""

    EMAIL_VERIFICATION = "email_verification_{user_id}"
    RESET_PASSWORD = "reset_password_{user_id}"
    PRODUCT_PARAMETERS_LIST = "product_parameters"
    ROLES_LIST = "roles"


class RedisNamesTTLEnum(IntEnum):
    """Redis names TTL enumerate."""

    EMAIL_VERIFICATION = 3600  # 1 hour
    RESET_PASSWORD = 3600  # 1 hour
    PRODUCT_PARAMETERS_LIST = 3600  # 1 hour
    ROLES_LIST = 3600  # 1 hour
