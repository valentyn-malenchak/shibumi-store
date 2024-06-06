"""Contains Pydantic utilities."""

import abc
from string import punctuation
from typing import Annotated, Any

from annotated_types import Gt
from bson import ObjectId
from pydantic import BaseModel, ConfigDict
from pydantic_core import PydanticCustomError, core_schema
from pydantic_extra_types.phone_numbers import PhoneNumber as PydanticPhoneNumber

from app.constants import ValidationErrorMessagesEnum


class ImmutableModel(BaseModel):
    """Immutable pydantic model."""

    model_config = ConfigDict(frozen=True)


class PhoneNumber(PydanticPhoneNumber):
    """Custom phone number data type."""

    phone_format = "E164"


class ObjectIdAnnotation:
    """BSON object identifier annotation."""

    @classmethod
    def _validate(cls, id_: Any, *_: Any) -> ObjectId:
        """Validates BSON object identifier."""

        if isinstance(id_, ObjectId):
            return id_

        if not ObjectId.is_valid(id_):
            raise PydanticCustomError(
                "object_id", ValidationErrorMessagesEnum.INVALID_IDENTIFIER
            )

        return ObjectId(id_)

    @classmethod
    def __get_pydantic_core_schema__(cls, *_: Any) -> core_schema.CoreSchema:
        """Customizes pydantic validation."""
        return core_schema.no_info_wrap_validator_function(
            cls._validate,
            core_schema.str_schema(),
            serialization=core_schema.to_string_ser_schema(),
        )


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

    __MIN_CHARACTERS_POLICY = 8

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

        if len(value) < cls.__MIN_CHARACTERS_POLICY:
            raise PydanticCustomError(
                "string_too_short",
                ValidationErrorMessagesEnum.PASSWORD_MIN_LENGTH,
            )

        if not any(char.isdigit() for char in value):
            raise PydanticCustomError(
                "string_without_digit",
                ValidationErrorMessagesEnum.PASSWORD_WITHOUT_DIGIT,
            )

        if not any(char.islower() for char in value):
            raise PydanticCustomError(
                "string_without_lowercase_letters",
                ValidationErrorMessagesEnum.PASSWORD_WITHOUT_LOWERCASE_LETTER,
            )

        if not any(char.isupper() for char in value):
            raise PydanticCustomError(
                "string_without_uppercase_letters",
                ValidationErrorMessagesEnum.PASSWORD_WITHOUT_UPPERCASE_LETTER,
            )

        if not any(char in punctuation for char in value):
            raise PydanticCustomError(
                "string_without_special_characters",
                ValidationErrorMessagesEnum.PASSWORD_WITHOUT_SPECIAL_CHARACTER,
            )

        return value


class UsernamePolicy(BaseType):
    """Username policy pydantic type."""

    __MIN_CHARACTERS_POLICY = 8
    __MAX_CHARACTERS_POLICY = 30
    __ALLOWED_SPECIAL_CHARACTER = "_-."

    @classmethod
    def _validate(cls, value: str, _: core_schema.ValidationInfo) -> str:
        """Validates username according to policy.

        Args:
            value (str): Username to validate.

        Returns:
            str: Username.

        Raises:
            PydanticCustomError: If username doesn't meet the requirements.

        """

        if len(value) < cls.__MIN_CHARACTERS_POLICY:
            raise PydanticCustomError(
                "string_too_short",
                ValidationErrorMessagesEnum.USERNAME_MIN_LENGTH,
            )

        if len(value) > cls.__MAX_CHARACTERS_POLICY:
            raise PydanticCustomError(
                "string_too_long", ValidationErrorMessagesEnum.USERNAME_MAX_LENGTH
            )

        if not all(
            char.isalnum() or char in cls.__ALLOWED_SPECIAL_CHARACTER for char in value
        ):
            raise PydanticCustomError(
                "string_with_not_permitted_characters",
                ValidationErrorMessagesEnum.USERNAME_NOT_ALLOWED_CHARACTERS,
            )

        return value


PositiveInt = Annotated[int, Gt(gt=0)]
