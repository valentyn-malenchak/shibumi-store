"""Contains cart domain dependencies."""

from typing import Annotated

from bson import ObjectId
from fastapi import Depends

from app.api.v1.models import ObjectIdAnnotation
from app.api.v1.models.cart import (
    AddCartProductRequestModel,
    UpdateCartProductRequestModel,
)
from app.api.v1.validators.cart import (
    CartAddProductValidator,
    CartDeleteProductValidator,
    CartUpdateProductValidator,
)


class CartProductAddDependency:
    """Cart product add dependency."""

    async def __call__(
        self,
        cart_product_data: AddCartProductRequestModel,
        cart_add_product_validator: CartAddProductValidator = Depends(),
    ) -> AddCartProductRequestModel:
        """Checks if cart product is valid on adding.

        Args:
            cart_product_data (AddCartProductRequestModel): Cart product request data.
            cart_add_product_validator (CartAddProductValidator): Cart add product
            validator.

        Returns:
            AddCartProductRequestModel: Cart product data.

        """

        await cart_add_product_validator.validate(
            product_id=cart_product_data.id, quantity=cart_product_data.quantity
        )

        return cart_product_data


class CartProductUpdateDependency:
    """Cart product update dependency."""

    async def __call__(
        self,
        product_id: Annotated[ObjectId, ObjectIdAnnotation],
        cart_product_data: UpdateCartProductRequestModel,
        cart_update_product_validator: CartUpdateProductValidator = Depends(),
    ) -> UpdateCartProductRequestModel:
        """Checks if cart product is valid on update.

        Args:
            product_id (Annotated[ObjectId, ObjectIdAnnotation]): BSON object
            identifier of requested product.
            cart_product_data (UpdateCartProductRequestModel): Cart product request
            data.
            cart_update_product_validator (CartUpdateProductValidator): Cart update
            product validator.

        Returns:
            UpdateCartProductRequestModel: Cart product data.

        """

        await cart_update_product_validator.validate(
            product_id=product_id, quantity=cart_product_data.quantity
        )

        return cart_product_data


class CartProductDeleteDependency:
    """Cart product update dependency."""

    async def __call__(
        self,
        product_id: Annotated[ObjectId, ObjectIdAnnotation],
        cart_delete_product_validator: CartDeleteProductValidator = Depends(),
    ) -> ObjectId:
        """Checks if cart product is valid on delete.

        Args:
            product_id (Annotated[ObjectId, ObjectIdAnnotation]): BSON object
            identifier of requested product.
            cart_delete_product_validator (CartDeleteProductValidator): Cart delete
            product validator.

        Returns:
            Cart: Current user cart.

        """

        await cart_delete_product_validator.validate(product_id=product_id)

        return product_id
