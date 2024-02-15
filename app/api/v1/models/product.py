"""Module that contains product domain models."""

from datetime import datetime
from typing import Annotated, Any, Dict

from bson import ObjectId
from pydantic import BaseModel

from app.api.v1.models import ObjectIdAnnotation, ObjectIdModel


class Product(ObjectIdModel):
    """Product model."""

    name: str
    synopsis: str
    description: str
    quantity: int
    category_id: Annotated[ObjectId, ObjectIdAnnotation]
    available: bool  # defines if product should be shown for customers
    html_body: str | None
    parameters: Dict[str, Any]
    created_at: datetime
    updated_at: datetime | None


class ProductResponseModel(ObjectIdModel):
    """Product response model."""

    name: str
    synopsis: str
    description: str
    quantity: int
    category_id: Annotated[ObjectId, ObjectIdAnnotation]
    available: bool
    html_body: str | None
    parameters: Dict[str, Any]
    created_at: datetime
    updated_at: datetime | None


class CreateProductRequestModel(BaseModel):
    """Product creation request model."""

    name: str
    synopsis: str
    description: str
    quantity: int
    category_id: Annotated[ObjectId, ObjectIdAnnotation]
    available: bool
    html_body: str | None
    parameters: Dict[str, Any]
