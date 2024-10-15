"""Module that contains category domain models."""

from datetime import datetime
from typing import Annotated

from bson import ObjectId
from pydantic import BaseModel, ConfigDict

from app.api.v1.models import BSONObjectId, List
from app.api.v1.models.parameter import Parameter
from app.utils.pydantic import ObjectIdAnnotation


class Category(BSONObjectId):
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


class ShortCategory(BSONObjectId):
    """Short category model."""

    name: str
    description: str
    parent_id: Annotated[ObjectId, ObjectIdAnnotation] | None
    path: str  # used as "Materialized Path" pattern
    machine_name: str
    created_at: datetime
    updated_at: datetime | None


class CategoryFilter(BaseModel):
    """Category list filter model."""

    path: str | None = None
    leafs: bool = False


class CategoryList(List):
    """Category list model."""

    data: list[ShortCategory]


class CategoryParameters(BSONObjectId):
    """Category parameters model."""

    model_config = ConfigDict(extra="allow")
