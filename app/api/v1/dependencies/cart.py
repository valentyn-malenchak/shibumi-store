"""Contains cart domain dependencies."""

from fastapi import Depends

from app.api.v1.models.cart import Cart, CartProduct
from app.api.v1.validators.cart import (
    CartAddProductValidator,
    CartProductValidator,
    CartUpdateProductValidator,
)


class CartProductDependency:
    """Cart product dependency."""

    async def __call__(
        self,
        cart_product: CartProduct,
        cart_product_validator: CartProductValidator = Depends(),
    ) -> CartProduct:
        """Checks cart product.

        Args:
            cart_product (CartProduct): Cart product.
            cart_product_validator (CartProductValidator): Cart product validator.

        Returns:
            CartProduct: Cart product.

        """

        return await cart_product_validator.validate(cart_product=cart_product)


class CartProductAddDependency:
    """Cart product add dependency."""

    async def __call__(
        self,
        cart_product: CartProduct,
        cart_add_product_validator: CartAddProductValidator = Depends(),
    ) -> Cart:
        """Checks if cart product is valid on adding.

        Args:
            cart_product (CartProduct): Cart product.
            cart_add_product_validator (CartAddProductValidator): Cart add product
            validator.

        Returns:
            Cart: Current user cart.

        """

        return await cart_add_product_validator.validate(cart_product=cart_product)


class CartProductUpdateDependency:
    """Cart product update dependency."""

    async def __call__(
        self,
        cart_product: CartProduct,
        cart_update_product_validator: CartUpdateProductValidator = Depends(),
    ) -> Cart:
        """Checks if cart product is valid on update.

        Args:
            cart_product (CartProduct): Cart product.
            cart_update_product_validator (CartUpdateProductValidator): Cart update
            product validator.

        Returns:
            Cart: Current user cart.

        """

        return await cart_update_product_validator.validate(cart_product=cart_product)
