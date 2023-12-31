"""Contains Pydantic utilities."""

from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field
from pydantic_extra_types.phone_numbers import PhoneNumber as PydanticPhoneNumber


class ObjectId(BaseModel):
    """Model that handles BSON ObjectID."""

    id: Annotated[str, BeforeValidator(str)] = Field(alias="_id")


class ImmutableModel(BaseModel):
    """Immutable pydantic model."""

    model_config = ConfigDict(frozen=True)


class PhoneNumber(PydanticPhoneNumber):
    """Custom phone number data type."""

    phone_format = "E164"
