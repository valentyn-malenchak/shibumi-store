"""Module that contains common domain models."""

from typing import Any, List

from pydantic import BaseModel, Field

from app.constants import PAGINATION_MAX_PAGE_SIZE, SortingTypesEnum


class SearchModel(BaseModel):
    """Search model for lists."""

    search: str | None = None


class PaginationModel(BaseModel):
    """Pagination model for lists."""

    page: int
    page_size: int = Field(le=PAGINATION_MAX_PAGE_SIZE)


class SortingModel(BaseModel):
    """Sorting model for lists."""

    # TODO: add fields list
    sort_by: str | None = None
    sort_order: SortingTypesEnum = SortingTypesEnum.ASC


class ListResponseModel(BaseModel):
    """List response model."""

    data: List[Any]
    total: int
