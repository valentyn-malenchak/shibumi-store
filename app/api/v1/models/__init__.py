"""Module that contains common domain models."""

from typing import Annotated, Any

from bson import ObjectId
from pydantic import AliasChoices, BaseModel, Field
from pydantic_core import PydanticCustomError, core_schema

from app.constants import (
    AppConstants,
    SortingTypesEnum,
    ValidationErrorMessagesEnum,
)


class ObjectIdAnnotation:
    """Object identifier annotation."""

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


class ObjectIdModel(BaseModel):
    """Model that handles BSON ObjectID."""

    id: Annotated[ObjectId, ObjectIdAnnotation] = Field(
        validation_alias=AliasChoices("_id", "id")
    )


class SearchModel(BaseModel):
    """Search model for lists."""

    search: str | None = None


class PaginationModel(BaseModel):
    """Pagination model for lists."""

    page: int
    page_size: int = Field(le=AppConstants.PAGINATION_MAX_PAGE_SIZE)


class SortingModel(BaseModel):
    """Sorting model for lists."""

    sort_by: str | None = None
    sort_order: SortingTypesEnum | None = None


class ListResponseModel(BaseModel):
    """List response model."""

    data: list[Any]
    total: int
