"""Contains cart domain dependencies."""

from typing import Annotated

from bson import ObjectId
from fastapi import Depends

from app.api.v1.dependencies.product import ProductAccessDependency
from app.api.v1.models.cart import (
    Cart,
    CartProduct,
    CartProductQuantity,
)
from app.api.v1.models.product import Product
from app.api.v1.validators.cart import (
    CartAccessValidator,
    CartByIdValidator,
    CartByUserValidator,
    CartProductValidator,
)
from app.api.v1.validators.product import (
    ProductAccessValidator,
    ProductByIdValidator,
    ProductQuantityValidator,
)
from app.utils.metas import SingletonMeta
from app.utils.pydantic import ObjectIdAnnotation


class CartByIdGetDependency(metaclass=SingletonMeta):
    """Cart by identifier get dependency."""

    async def __call__(
        self,
        cart_id: Annotated[ObjectId, ObjectIdAnnotation],
        cart_by_id_validator: CartByIdValidator = Depends(),
    ) -> Cart:
        """Validates cart by its unique identifier.

        Args:
            cart_id (Annotated[ObjectId, ObjectIdAnnotation]): BSON object
            identifier of requested cart.
            cart_by_id_validator (CartByIdValidator): Cart by identifier validator.

        Returns:
            Cart: Cart object.

        """
        return await cart_by_id_validator.validate(cart_id=cart_id)


class CartAccessDependency(metaclass=SingletonMeta):
    """Cart access dependency."""

    async def __call__(
        self,
        cart: Cart = Depends(CartByIdGetDependency()),
        cart_access_validator: CartAccessValidator = Depends(),
    ) -> Cart:
        """Validates access to specific cart.

        Args:
            cart (Cart): Cart object.
            cart_access_validator (CartAccessValidator): Cart access validator.

        Returns:
            Cart: Cart object.

        """
        return await cart_access_validator.validate(cart=cart)


class CartByUserGetDependency(metaclass=SingletonMeta):
    """Cart by user get dependency."""

    async def __call__(
        self,
        cart_by_user_validator: CartByUserValidator = Depends(),
    ) -> Cart:
        """Validates cart of current user.

        Args:
            cart_by_user_validator (CartByUserValidator): Cart by user validator.

        Returns:
            Cart: Cart object.

        """
        return await cart_by_user_validator.validate()


class CartProductDataCreateDependency(metaclass=SingletonMeta):
    """Cart product data create dependency."""

    async def __call__(  # noqa: PLR0913
        self,
        cart_product: CartProduct,
        cart: Cart = Depends(CartAccessDependency()),
        product_by_id_validator: ProductByIdValidator = Depends(),
        product_access_validator: ProductAccessValidator = Depends(),
        product_quantity_validator: ProductQuantityValidator = Depends(),
        cart_product_validator: CartProductValidator = Depends(),
    ) -> CartProduct:
        """Validates if cart product data is valid on create.

        Args:
            cart_product (CartProduct): Cart product.
            cart (Cart): Cart object.
            product_by_id_validator (ProductByIdValidator): Product by identifier
            validator.
            product_access_validator (ProductAccessValidator): Product access validator.
            product_quantity_validator (ProductQuantityValidator): Product quantity
            validator.
            cart_product_validator (CartProductValidator): Cart product validator.

        Returns:
            CartProduct: Cart product.

        """

        product = await product_by_id_validator.validate(product_id=cart_product.id)

        await product_access_validator.validate(product=product)

        await product_quantity_validator.validate(
            product=product, quantity=cart_product.quantity
        )

        await cart_product_validator.validate(
            product_id=cart_product.id, cart=cart, negative=True
        )

        return cart_product


class CartProductDataUpdateDependency(metaclass=SingletonMeta):
    """Cart product data update dependency."""

    async def __call__(
        self,
        cart_product_quantity: CartProductQuantity,
        product: Product = Depends(ProductAccessDependency()),
        cart: Cart = Depends(CartAccessDependency()),
        product_quantity_validator: ProductQuantityValidator = Depends(),
        cart_product_validator: CartProductValidator = Depends(),
    ) -> CartProductQuantity:
        """Validates if cart product data is valid on update.

        Args:
            cart_product_quantity (CartProductQuantity): Cart product quantity.
            product (Product): Product object.
            cart (Cart): Cart object.
            product_quantity_validator (ProductQuantityValidator): Product quantity
            validator.
            cart_product_validator (CartProductValidator): Cart product validator.

        Returns:
            CartProductQuantity: Cart product quantity.

        """

        await product_quantity_validator.validate(
            product=product, quantity=cart_product_quantity.quantity
        )

        await cart_product_validator.validate(product_id=product.id, cart=cart)

        return cart_product_quantity


class CartProductDataDeleteDependency(metaclass=SingletonMeta):
    """Cart product data delete dependency."""

    async def __call__(
        self,
        product: Product = Depends(ProductAccessDependency()),
        cart: Cart = Depends(CartAccessDependency()),
        cart_product_validator: CartProductValidator = Depends(),
    ) -> ObjectId:
        """Validates if cart product data is valid on delete.

        Args:
            product (Product): Product object.
            cart (Cart): Cart object.
            cart_product_validator (CartProductValidator): Cart product validator.

        Returns:
            ObjectId: BSON object identifier of requested product.

        """

        await cart_product_validator.validate(product_id=product.id, cart=cart)

        return product.id
