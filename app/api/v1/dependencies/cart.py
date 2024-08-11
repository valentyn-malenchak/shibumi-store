"""Contains cart domain dependencies."""

from typing import Annotated

from bson import ObjectId
from fastapi import Depends

from app.api.v1.models.cart import (
    Cart,
    CartProduct,
    CartProductQuantity,
)
from app.api.v1.validators.cart import (
    CartByIdValidator,
    CartByUserValidator,
    CartProductAddValidator,
    CartProductDeleteValidator,
    CartProductUpdateValidator,
)
from app.utils.pydantic import ObjectIdAnnotation


class CartByIdDependency:
    """Cart by identifier dependency."""

    async def __call__(
        self,
        cart_id: Annotated[ObjectId, ObjectIdAnnotation],
        cart_by_id_validator: CartByIdValidator = Depends(),
    ) -> Cart:
        """Validates cart from request by identifier.

        Args:
            cart_id (Annotated[ObjectId, ObjectIdAnnotation]): BSON object
            identifier of requested cart.
            cart_by_id_validator (CartByIdValidator): Cart by identifier validator.

        Returns:
            Cart: Cart object.

        """

        return await cart_by_id_validator.validate(cart_id=cart_id)


class CartByUserDependency:
    """Cart by user dependency."""

    async def __call__(
        self,
        cart_by_user_validator: CartByUserValidator = Depends(),
    ) -> Cart:
        """Validates cart by requested user.

        Args:
            cart_by_user_validator (CartByUserValidator): Cart by user validator.

        Returns:
            Cart: Cart object.

        """

        return await cart_by_user_validator.validate()


class CartProductAddDependency:
    """Cart product add dependency."""

    async def __call__(
        self,
        cart_product: CartProduct,
        cart_product_add_validator: CartProductAddValidator = Depends(),
    ) -> CartProduct:
        """Validates if cart product is valid on adding.

        Args:
            cart_product (CartProduct): Cart product request data.
            cart_product_add_validator (CartProductAddValidator): Cart add product
            validator.

        Returns:
            CartProduct: Cart product.

        """

        await cart_product_add_validator.validate(
            product_id=cart_product.id, quantity=cart_product.quantity
        )

        return cart_product


class CartProductUpdateDependency:
    """Cart product update dependency."""

    async def __call__(
        self,
        product_id: Annotated[ObjectId, ObjectIdAnnotation],
        cart_product_quantity: CartProductQuantity,
        cart_product_update_validator: CartProductUpdateValidator = Depends(),
    ) -> CartProductQuantity:
        """Validates if cart product is valid on update.

        Args:
            product_id (Annotated[ObjectId, ObjectIdAnnotation]): BSON object
            identifier of requested product.
            cart_product_quantity (CartProductQuantity): Cart product quantity
            request data.
            cart_product_update_validator (CartProductUpdateValidator): Cart update
            product validator.

        Returns:
            CartProductQuantity: Cart product quantity.

        """

        await cart_product_update_validator.validate(
            product_id=product_id, quantity=cart_product_quantity.quantity
        )

        return cart_product_quantity


class CartProductDeleteDependency:
    """Cart product update dependency."""

    async def __call__(
        self,
        product_id: Annotated[ObjectId, ObjectIdAnnotation],
        cart_product_delete_validator: CartProductDeleteValidator = Depends(),
    ) -> ObjectId:
        """Validates if cart product is valid on delete.

        Args:
            product_id (Annotated[ObjectId, ObjectIdAnnotation]): BSON object
            identifier of requested product.
            cart_product_delete_validator (CartProductDeleteValidator): Cart delete
            product validator.

        Returns:
            ObjectId: BSON object identifier of requested product.

        """

        await cart_product_delete_validator.validate(product_id=product_id)

        return product_id
