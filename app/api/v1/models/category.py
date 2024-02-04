"""Module that contains category domain models."""

from datetime import datetime
from typing import Annotated, List

from bson import ObjectId
from pydantic import BaseModel, Field

from app.api.v1.models import ListResponseModel, ObjectIdAnnotation, ObjectIdModel


class Category(ObjectIdModel):
    """Category response model."""

    name: str
    description: str
    # TODO: check if alias is needed
    parent_id: Annotated[ObjectId, ObjectIdAnnotation] | None = Field()
    path: str  # used as "Materialized Path" pattern
    path_name: str
    created_at: datetime
    updated_at: datetime | None


class CategoriesFilterModel(BaseModel):
    """Categories list filter model."""

    path: str | None = None


class CategoriesListModel(ListResponseModel):
    """Categories list model."""

    data: List[Category]
