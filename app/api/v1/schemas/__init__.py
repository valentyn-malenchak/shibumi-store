"""Module that contains common domain schemas."""

from typing import Annotated

from pydantic import BaseModel, BeforeValidator, Field


class ObjectId(BaseModel):
    """Model that handles BSON ObjectID."""

    id: Annotated[str, BeforeValidator(str)] = Field(alias="_id")
