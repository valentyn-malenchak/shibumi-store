"""Module that contains cart domain models."""

from datetime import datetime
from typing import Annotated

from bson import ObjectId
from pydantic import BaseModel

from app.api.v1.models import BSONObjectId
from app.api.v1.models.product import Product
from app.utils.pydantic import ObjectIdAnnotation, PositiveInt


class CartProductQuantity(BaseModel):
    """Cart product quantity model."""

    quantity: PositiveInt


class CartProduct(BSONObjectId):
    """Cart product model."""

    quantity: PositiveInt


class Cart(BSONObjectId):
    """Cart model."""

    user_id: Annotated[ObjectId, ObjectIdAnnotation]
    products: list[CartProduct]
    created_at: datetime
    updated_at: datetime | None


class CartCreateData(BaseModel):
    """Cart create data model."""

    user_id: Annotated[ObjectId, ObjectIdAnnotation]


class CartProductCreateData(BaseModel):
    """Cart product create data."""

    cart: Cart
    cart_product: CartProduct


class CartProductUpdateData(BaseModel):
    """Cart product update data."""

    cart: Cart
    product: Product
    cart_product_quantity: CartProductQuantity
