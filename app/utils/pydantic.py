"""Contains Pydantic utilities."""

from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field


class ObjectId(BaseModel):
    """Model that handles BSON ObjectID."""

    id: Annotated[str, BeforeValidator(str)] = Field(alias="_id")


class ImmutableModel(BaseModel):
    """Immutable pydantic model."""

    model_config = ConfigDict(frozen=True)
