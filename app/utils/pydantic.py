"""Contains Pydantic utilities."""

from string import punctuation
from typing import Annotated, Any

from pydantic import AliasChoices, BaseModel, BeforeValidator, ConfigDict, Field
from pydantic_core import PydanticCustomError, core_schema
from pydantic_extra_types.phone_numbers import PhoneNumber as PydanticPhoneNumber

from app.constants import (
    PASSWORD_MIN_CHARACTERS_POLICY,
    USERNAME_ALLOWED_SPECIAL_CHARACTER,
    USERNAME_MAX_CHARACTERS_POLICY,
    USERNAME_MIN_CHARACTERS_POLICY,
    ValidationErrorMessagesEnum,
)


class ObjectId(BaseModel):
    """Model that handles BSON ObjectID."""

    id: Annotated[str, BeforeValidator(str)] = Field(
        validation_alias=AliasChoices("_id", "id")
    )


class ImmutableModel(BaseModel):
    """Immutable pydantic model."""

    model_config = ConfigDict(frozen=True)


class PhoneNumber(PydanticPhoneNumber):
    """Custom phone number data type."""

    phone_format = "E164"


class BaseStringType(str):
    """Base String pydantic type."""

    @classmethod
    def __get_pydantic_core_schema__(cls, *_: Any) -> core_schema.CoreSchema:
        """Customizes pydantic validation."""
        return core_schema.with_info_after_validator_function(
            cls._validate,
            core_schema.str_schema(),
        )

    @classmethod
    def _validate(cls, value: str, _: core_schema.ValidationInfo) -> str:
        """Validates a value."""
        raise NotImplementedError


class PasswordPolicy(BaseStringType):
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


class UsernamePolicy(BaseStringType):
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
