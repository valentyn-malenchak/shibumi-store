"""Module that contains category domain models."""

from datetime import datetime
from typing import Annotated

from bson import ObjectId
from pydantic import BaseModel, ConfigDict

from app.api.v1.models import ListResponseModel, ObjectIdAnnotation, ObjectIdModel
from app.api.v1.models.parameter import Parameter


class Category(ObjectIdModel):
    """Category model."""

    name: str
    description: str
    parent_id: Annotated[ObjectId, ObjectIdAnnotation] | None
    path: str  # used as "Materialized Path" pattern
    machine_name: str
    has_children: bool
    parameters: list[Parameter]
    created_at: datetime
    updated_at: datetime | None


class ShortCategoryResponseModel(ObjectIdModel):
    """Short category response model."""

    name: str
    description: str
    parent_id: Annotated[ObjectId, ObjectIdAnnotation] | None
    path: str  # used as "Materialized Path" pattern
    machine_name: str
    created_at: datetime
    updated_at: datetime | None


class ExtendedCategoryResponseModel(ShortCategoryResponseModel):
    """Extended category response model."""

    parameters: list[Parameter]


class CategoriesFilterModel(BaseModel):
    """Categories list filter model."""

    path: str | None = None
    leafs: bool = False


class CategoriesListModel(ListResponseModel):
    """Categories list model."""

    data: list[ShortCategoryResponseModel]


class CategoryParametersResponseModel(ObjectIdModel):
    """Category parameters response model."""

    model_config = ConfigDict(extra="allow")
