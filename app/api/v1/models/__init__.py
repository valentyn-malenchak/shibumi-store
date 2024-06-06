"""Module that contains common domain models."""

from typing import Annotated, Any

from bson import ObjectId
from pydantic import AliasChoices, BaseModel, Field

from app.constants import (
    AppConstants,
    SortingTypesEnum,
)
from app.utils.pydantic import ObjectIdAnnotation


class BSONObjectId(BaseModel):
    """Model that handles BSON ObjectID."""

    id: Annotated[ObjectId, ObjectIdAnnotation] = Field(
        validation_alias=AliasChoices("_id", "id")
    )


class Search(BaseModel):
    """Search model for lists."""

    search: str | None = None


class Pagination(BaseModel):
    """Pagination model for lists."""

    page: int
    page_size: int = Field(le=AppConstants.PAGINATION_MAX_PAGE_SIZE)


class Sorting(BaseModel):
    """Sorting model for lists."""

    sort_by: str | None = None
    sort_order: SortingTypesEnum | None = None


class List(BaseModel):
    """List model."""

    data: list[Any]
    total: int
