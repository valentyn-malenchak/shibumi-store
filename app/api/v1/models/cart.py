"""Module that contains cart domain models."""

from datetime import datetime
from typing import Annotated

from bson import ObjectId
from pydantic import BaseModel

from app.api.v1.models import ObjectIdAnnotation, ObjectIdModel
from app.utils.pydantic import PositiveInt


class AddCartProductRequestModel(ObjectIdModel):
    """Add cart product request model."""

    quantity: PositiveInt


class UpdateCartProductRequestModel(BaseModel):
    """Update cart product request model."""

    quantity: PositiveInt


class CartProduct(ObjectIdModel):
    """Cart product model."""

    quantity: PositiveInt


class Cart(ObjectIdModel):
    """Cart model."""

    user_id: Annotated[ObjectId, ObjectIdAnnotation]
    products: list[CartProduct]
    created_at: datetime
    updated_at: datetime | None


class CartResponseModel(ObjectIdModel):
    """Cart response model."""

    user_id: Annotated[ObjectId, ObjectIdAnnotation]
    products: list[CartProduct]
    created_at: datetime
    updated_at: datetime | None