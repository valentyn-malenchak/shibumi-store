"""Module that contains product domain models."""

from datetime import datetime
from typing import Annotated, Any

from bson import ObjectId
from fastapi import Query
from pydantic import BaseModel, Field

from app.api.v1.models import ListResponseModel, ObjectIdAnnotation, ObjectIdModel


class Product(ObjectIdModel):
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
    created_at: datetime
    updated_at: datetime | None


class ShortProductResponseModel(ObjectIdModel):
    """Short product response model."""

    name: str
    synopsis: str
    quantity: int
    price: float
    views: int
    category_id: Annotated[ObjectId, ObjectIdAnnotation]
    available: bool
    created_at: datetime
    updated_at: datetime | None


class ExtendedProductResponseModel(ShortProductResponseModel):
    """Extended product response model."""

    description: str
    html_body: str | None
    parameters: dict[str, Any]


class BaseProductsFilterModel(BaseModel):
    """Base products list filter model."""

    category_id: Annotated[ObjectId, ObjectIdAnnotation] | None = None
    available: bool | None = None
    ids: list[Annotated[ObjectId, ObjectIdAnnotation]] | None = Field(Query([]))


class ProductsFilterModel(BaseProductsFilterModel):
    """Products list filter model."""

    parameters: dict[str, list[Any]] | None = None


class ProductsListModel(ListResponseModel):
    """Products list model."""

    data: list[ShortProductResponseModel]


class ProductRequestModel(BaseModel):
    """Create/update product request model."""

    name: str
    synopsis: str
    description: str
    quantity: int
    price: float
    category_id: Annotated[ObjectId, ObjectIdAnnotation]
    available: bool
    html_body: str | None
    parameters: dict[str, Any]
