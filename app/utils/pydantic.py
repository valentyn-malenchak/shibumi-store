"""Contains Pydantic utilities."""

import abc
from string import punctuation
from typing import Any

from pydantic import BaseModel, ConfigDict
from pydantic_core import PydanticCustomError, core_schema
from pydantic_extra_types.phone_numbers import PhoneNumber as PydanticPhoneNumber

from app.constants import (
    PASSWORD_MIN_CHARACTERS_POLICY,
    USERNAME_ALLOWED_SPECIAL_CHARACTER,
    USERNAME_MAX_CHARACTERS_POLICY,
    USERNAME_MIN_CHARACTERS_POLICY,
    ValidationErrorMessagesEnum,
)


class ImmutableModel(BaseModel):
    """Immutable pydantic model."""

    model_config = ConfigDict(frozen=True)


class PhoneNumber(PydanticPhoneNumber):
    """Custom phone number data type."""

    phone_format = "E164"


class BaseType(str):
    """Base pydantic type."""

    @classmethod
    def __get_pydantic_core_schema__(cls, *_: Any) -> core_schema.CoreSchema:
        """Customizes pydantic validation."""
        return core_schema.with_info_after_validator_function(
            cls._validate,
            core_schema.str_schema(),
        )

    @classmethod
    @abc.abstractmethod
    def _validate(cls, value: str, _: core_schema.ValidationInfo) -> str:
        """Validates a value."""
        raise NotImplementedError


class PasswordPolicy(BaseType):
    """Password policy pydantic type."""

    @classmethod
    def _validate(cls, value: str, _: core_schema.ValidationInfo) -> str:
        """Validates password according to policy.

        Args:
            value (str): Password to validate.

        Returns:
            str: Password.

        Raises:
            PydanticCustomError: If password doesn't meet the requirements.

        """

        if len(value) < PASSWORD_MIN_CHARACTERS_POLICY:
            raise PydanticCustomError(
                "string_too_short",
                ValidationErrorMessagesEnum.PASSWORD_MIN_LENGTH.value,
            )

        if not any(char.isdigit() for char in value):
            raise PydanticCustomError(
                "string_without_digit",
                ValidationErrorMessagesEnum.PASSWORD_WITHOUT_DIGIT.value,
            )

        if not any(char.islower() for char in value):
            raise PydanticCustomError(
                "string_without_lowercase_letters",
                ValidationErrorMessagesEnum.PASSWORD_WITHOUT_LOWERCASE_LETTER.value,
            )

        if not any(char.isupper() for char in value):
            raise PydanticCustomError(
                "string_without_uppercase_letters",
                ValidationErrorMessagesEnum.PASSWORD_WITHOUT_UPPERCASE_LETTER.value,
            )

        if not any(char in punctuation for char in value):
            raise PydanticCustomError(
                "string_without_special_characters",
                ValidationErrorMessagesEnum.PASSWORD_WITHOUT_SPECIAL_CHARACTER.value,
            )

        return value


class UsernamePolicy(BaseType):
    """Username policy pydantic type."""

    @classmethod
    def _validate(cls, value: str, _: core_schema.ValidationInfo) -> str:
        """Validates username according to policy.

        Args:
            value (str): Username to validate.

        Returns:
            str: Username.

        Raises:
            ValueError: If username doesn't meet the requirements.

        """

        if len(value) < USERNAME_MIN_CHARACTERS_POLICY:
            raise PydanticCustomError(
                "string_too_short",
                ValidationErrorMessagesEnum.USERNAME_MIN_LENGTH.value,
            )

        if len(value) > USERNAME_MAX_CHARACTERS_POLICY:
            raise PydanticCustomError(
                "string_too_long", ValidationErrorMessagesEnum.USERNAME_MAX_LENGTH.value
            )

        if not all(
            char.isalnum() or char in USERNAME_ALLOWED_SPECIAL_CHARACTER
            for char in value
        ):
            raise PydanticCustomError(
                "string_with_not_permitted_characters",
                ValidationErrorMessagesEnum.USERNAME_NOT_ALLOWED_CHARACTERS.value,
            )

        return value
