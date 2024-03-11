"""Module that contains product domain models."""

from datetime import datetime
from typing import Annotated, Any, Dict, List

from bson import ObjectId
from pydantic import BaseModel

from app.api.v1.models import ListResponseModel, ObjectIdAnnotation, ObjectIdModel


class Product(ObjectIdModel):
    """Product model."""

    name: str
    synopsis: str
    description: str
    quantity: int
    price: float
    category_id: Annotated[ObjectId, ObjectIdAnnotation]
    available: bool  # defines if product should be shown for customers
    html_body: str | None
    parameters: Dict[str, Any]
    created_at: datetime
    updated_at: datetime | None


class ShortProductResponseModel(ObjectIdModel):
    """Short product response model."""

    name: str
    synopsis: str
    quantity: int
    price: float
    category_id: Annotated[ObjectId, ObjectIdAnnotation]
    available: bool
    created_at: datetime
    updated_at: datetime | None


class ExtendedProductResponseModel(ShortProductResponseModel):
    """Extended product response model."""

    description: str
    html_body: str | None
    parameters: Dict[str, Any]


class BaseProductsFilterModel(BaseModel):
    """Base products list filter model."""

    category_id: Annotated[ObjectId, ObjectIdAnnotation] | None = None
    available: bool | None = None


class ProductsFilterModel(BaseProductsFilterModel):
    """Products list filter model."""

    parameters: Dict[str, List[Any]] | None = None


class ProductsListModel(ListResponseModel):
    """Products list model."""

    data: List[ShortProductResponseModel]


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
    parameters: Dict[str, Any]
