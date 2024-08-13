"""Contains cart domain dependencies."""

from typing import Annotated

from bson import ObjectId
from fastapi import Depends

from app.api.v1.dependencies.product import ProductByIdGetAccessDependency
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


class CartByIdGetAccessDependency(metaclass=SingletonMeta):
    """Cart by identifier get access dependency."""

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


class CartProductAddQuantityDependency(metaclass=SingletonMeta):
    """Cart product add quantity dependency."""

    async def __call__(
        self,
        cart_product: CartProduct,
        product_by_id_validator: ProductByIdValidator = Depends(),
        product_access_validator: ProductAccessValidator = Depends(),
        product_quantity_validator: ProductQuantityValidator = Depends(),
    ) -> CartProduct:
        """Validates product quantity available on add to cart operation.

        Args:
            cart_product (CartProduct): Cart product.
            product_by_id_validator (ProductByIdValidator): Product by identifier
            validator.
            product_access_validator (ProductAccessValidator): Product access validator.
            product_quantity_validator (ProductQuantityValidator): Product quantity
            validator.

        Returns:
            CartProduct: Cart product.

        """

        product = await product_by_id_validator.validate(product_id=cart_product.id)

        await product_access_validator.validate(product=product)

        await product_quantity_validator.validate(
            product=product, quantity=cart_product.quantity
        )

        return cart_product


class CartProductUpdateQuantityDependency(metaclass=SingletonMeta):
    """Cart product update quantity dependency."""

    async def __call__(
        self,
        cart_product_quantity: CartProductQuantity,
        product: Product = Depends(ProductByIdGetAccessDependency()),
        product_quantity_validator: ProductQuantityValidator = Depends(),
    ) -> CartProductQuantity:
        """Validates product quantity available on update in cart operation.

        Args:
            cart_product_quantity (CartProductQuantity): Cart product quantity.
            product (Product): Product object.
            product_quantity_validator (ProductQuantityValidator): Product quantity
            validator.

        Returns:
            CartProductQuantity: Cart product quantity.

        """

        await product_quantity_validator.validate(
            product=product, quantity=cart_product_quantity.quantity
        )

        return cart_product_quantity


class CartProductAddDataDependency(metaclass=SingletonMeta):
    """Cart product add data dependency."""

    async def __call__(
        self,
        cart_product: CartProduct = Depends(CartProductAddQuantityDependency()),
        cart: Cart = Depends(CartByIdGetAccessDependency()),
        cart_product_validator: CartProductValidator = Depends(),
    ) -> CartProduct:
        """Validates if cart product data is valid on adding.

        Args:
            cart_product (CartProduct): Cart product.
            cart (Cart): Cart object.
            cart_product_validator (CartProductValidator): Cart product validator.

        Returns:
            CartProduct: Cart product.

        """

        await cart_product_validator.validate(
            product_id=cart_product.id, cart=cart, negative=True
        )

        return cart_product


class CartProductUpdateDataDependency(metaclass=SingletonMeta):
    """Cart product update data dependency."""

    async def __call__(
        self,
        cart_product_quantity: CartProductQuantity = Depends(
            CartProductUpdateQuantityDependency()
        ),
        cart: Cart = Depends(CartByIdGetAccessDependency()),
        product: Product = Depends(ProductByIdGetAccessDependency()),
        cart_product_validator: CartProductValidator = Depends(),
    ) -> CartProductQuantity:
        """Validates if cart product data is valid on update.

        Args:
            cart_product_quantity (CartProductQuantity): Cart product quantity.
            cart (Cart): Cart object.
            product (Product): Product object.
            cart_product_validator (CartProductValidator): Cart product validator.

        Returns:
            CartProductQuantity: Cart product quantity.

        """

        await cart_product_validator.validate(product_id=product.id, cart=cart)

        return cart_product_quantity


class CartProductDeleteDataDependency(metaclass=SingletonMeta):
    """Cart product delete data dependency."""

    async def __call__(
        self,
        product: Product = Depends(ProductByIdGetAccessDependency()),
        cart: Cart = Depends(CartByIdGetAccessDependency()),
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
