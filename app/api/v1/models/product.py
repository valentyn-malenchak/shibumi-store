"""Module that contains product domain models."""

from datetime import datetime
from typing import Annotated, Any

from bson import ObjectId
from fastapi import Query
from pydantic import BaseModel, Field

from app.api.v1.models import BSONObjectId, List, ObjectIdAnnotation


class ProductData(BaseModel):
    """Product data model."""

    name: str
    synopsis: str
    description: str
    quantity: int
    price: float
    category_id: Annotated[ObjectId, ObjectIdAnnotation]
    available: bool
    html_body: str | None
    parameters: dict[str, Any]


class ProductCreateData(ProductData):
    """Product create data model."""

    thread_id: Annotated[ObjectId, ObjectIdAnnotation]


class Product(BSONObjectId):
    """Product model."""

    name: str
    synopsis: str
    description: str
    quantity: int
    price: float
    views: int
    category_id: Annotated[ObjectId, ObjectIdAnnotation]
    available: bool  # defines if product should be shown for customers
    html_body: str | None
    parameters: dict[str, Any]
    thread_id: Annotated[ObjectId, ObjectIdAnnotation]
    created_at: datetime
    updated_at: datetime | None


class ShortProduct(BSONObjectId):
    """Short product model."""

    name: str
    synopsis: str
    quantity: int
    price: float
    views: int
    category_id: Annotated[ObjectId, ObjectIdAnnotation]
    available: bool
    created_at: datetime
    updated_at: datetime | None


class BaseProductFilter(BaseModel):
    """Base product filter model."""

    category_id: Annotated[ObjectId, ObjectIdAnnotation] | None = None
    available: bool | None = None
    ids: list[Annotated[ObjectId, ObjectIdAnnotation]] | None = Field(
        Query(default_factory=list)
    )


class ProductFilter(BaseProductFilter):
    """Product filter model."""

    parameters: dict[str, list[Any]] | None = None


class ProductList(List):
    """Product list model."""

    data: list[ShortProduct]
