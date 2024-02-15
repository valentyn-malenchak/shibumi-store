"""Module that contains category domain models."""

from datetime import datetime
from typing import Annotated, List

from bson import ObjectId
from pydantic import BaseModel

from app.api.v1.models import ListResponseModel, ObjectIdAnnotation, ObjectIdModel


class Parameter(ObjectIdModel):
    """Parameter model."""

    name: str
    machine_name: str
    type: str
    created_at: datetime
    updated_at: datetime | None


class Category(ObjectIdModel):
    """Category model."""

    name: str
    description: str
    parent_id: Annotated[ObjectId, ObjectIdAnnotation] | None
    path: str  # used as "Materialized Path" pattern
    path_name: str
    has_children: bool
    parameters: List[Parameter]
    created_at: datetime
    updated_at: datetime | None


class CategoryResponseModel(ObjectIdModel):
    """Category response model."""

    name: str
    description: str
    parent_id: Annotated[ObjectId, ObjectIdAnnotation] | None
    path: str  # used as "Materialized Path" pattern
    path_name: str


class CategoriesFilterModel(BaseModel):
    """Categories list filter model."""

    path: str | None = None
    leafs: bool = False


class CategoriesListModel(ListResponseModel):
    """Categories list model."""

    data: List[CategoryResponseModel]
