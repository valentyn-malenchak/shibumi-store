"""Contains cart domain validators."""

from typing import Any

from fastapi import Depends, HTTPException, Request, status

from app.api.v1.models.cart import CartProduct
from app.api.v1.services.cart import Cart, CartService
from app.api.v1.validators import BaseValidator
from app.api.v1.validators.product import ProductByIdStatusValidator
from app.constants import HTTPErrorMessagesEnum


class BaseCartValidator(BaseValidator):
    """Base cart validator."""

    def __init__(self, request: Request, cart_service: CartService = Depends()):
        """Initializes base cart validator.

        Args:
            request (Request): Current request object.
            cart_service (CartService): Cart service.

        """

        super().__init__(request=request)

        self.cart_service = cart_service

    async def validate(self, *args: Any) -> Any:
        """Validates data.

        Args:
            args (Any): Method arguments.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.

        """
        raise NotImplementedError


class CartProductValidator(BaseCartValidator):
    """Cart product validator."""

    def __init__(
        self,
        request: Request,
        cart_service: CartService = Depends(),
        product_by_id_status_validator: ProductByIdStatusValidator = Depends(),
    ):
        """Initializes product parameters validator.

        Args:
            request (Request): Current request object.
            cart_service (CartService): Cart service.
            product_by_id_status_validator (ProductByIdStatusValidator): Product by
            identifier status validator.

        """

        super().__init__(request=request, cart_service=cart_service)

        self.product_by_id_status_validator = product_by_id_status_validator

    async def validate(self, cart_product: CartProduct) -> CartProduct:
        """Validates cart product.

        Args:
            cart_product (CartProduct): Cart product to validate.

        Returns:
            CartProduct: Cart product.

        Raises:
            HTTPException: If cart product quantity is exceeded the maximum number
            available.

        """

        product = await self.product_by_id_status_validator.validate(
            product_id=cart_product.id
        )

        if product.quantity < cart_product.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=HTTPErrorMessagesEnum.MAXIMUM_PRODUCT_QUANTITY_AVAILABLE,
            )

        return cart_product


class CartAddProductValidator(BaseCartValidator):
    """Cart add product validator."""

    async def validate(self, cart_product: CartProduct) -> Cart:
        """Validates product on adding it to the cart.

        Args:
            cart_product (CartProduct): Cart product to validate.

        Returns:
            Cart: Current user cart.

        """

        current_user = self.request.state.current_user

        cart = await self.cart_service.get_by_user_id(user_id=current_user.object.id)

        if cart_product.id in {product.id for product in cart.products}:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=HTTPErrorMessagesEnum.PRODUCT_IS_ALREADY_ADDED_TO_THE_CART,
            )

        return cart


class CartUpdateProductValidator(BaseCartValidator):
    """Cart update product validator."""

    async def validate(self, cart_product: CartProduct) -> Cart:
        """Validates product on updating it in the cart.

        Args:
            cart_product (CartProduct): Cart product to validate.

        Returns:
            Cart: Current user cart.

        """

        current_user = self.request.state.current_user

        cart = await self.cart_service.get_by_user_id(user_id=current_user.object.id)

        if cart_product.id not in {product.id for product in cart.products}:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=HTTPErrorMessagesEnum.PRODUCT_IS_NOT_ADDED_TO_THE_CART,
            )

        return cart
