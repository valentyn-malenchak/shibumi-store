"""Contains cart domain validators."""

from typing import Any

from bson import ObjectId
from fastapi import Depends, HTTPException, Request, status

from app.api.v1.services.cart import CartService
from app.api.v1.validators import BaseValidator
from app.api.v1.validators.product import (
    ProductByIdStatusValidator,
    ProductQuantityValidator,
)
from app.constants import HTTPErrorMessagesEnum
from app.utils.pydantic import PositiveInt


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


class CartAddProductValidator(BaseCartValidator):
    """Cart add product validator."""

    def __init__(
        self,
        request: Request,
        cart_service: CartService = Depends(),
        product_quantity_validator: ProductQuantityValidator = Depends(),
    ):
        """Initializes cart add product validator.

        Args:
            request (Request): Current request object.
            cart_service (CartService): Cart service.
            product_quantity_validator (ProductQuantityValidator): Product quantity
            validator.

        """

        super().__init__(request=request, cart_service=cart_service)

        self.product_quantity_validator = product_quantity_validator

    async def validate(self, product_id: ObjectId, quantity: PositiveInt) -> None:
        """Validates product on adding it to the cart.

        Args:
            product_id (ObjectId): BSON object identifier of requested product.
            quantity (PositiveInt): Product quantity.

        """

        await self.product_quantity_validator.validate(
            product_id=product_id, quantity=quantity
        )

        current_user = self.request.state.current_user

        cart = await self.cart_service.get_by_user_id(user_id=current_user.object.id)

        if product_id in {cart_product.id for cart_product in cart.products}:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=HTTPErrorMessagesEnum.PRODUCT_IS_ALREADY_ADDED_TO_THE_CART,
            )


class CartUpdateProductValidator(BaseCartValidator):
    """Cart update product validator."""

    def __init__(
        self,
        request: Request,
        cart_service: CartService = Depends(),
        product_quantity_validator: ProductQuantityValidator = Depends(),
    ):
        """Initializes cart update product validator.

        Args:
            request (Request): Current request object.
            cart_service (CartService): Cart service.
            product_quantity_validator (ProductQuantityValidator): Product quantity
            validator.

        """

        super().__init__(request=request, cart_service=cart_service)

        self.product_quantity_validator = product_quantity_validator

    async def validate(self, product_id: ObjectId, quantity: PositiveInt) -> None:
        """Validates product on updating it in the cart.

        Args:
            product_id (ObjectId): BSON object identifier of requested product.
            quantity (PositiveInt): Product quantity.

        """

        await self.product_quantity_validator.validate(
            product_id=product_id, quantity=quantity
        )

        current_user = self.request.state.current_user

        cart = await self.cart_service.get_by_user_id(user_id=current_user.object.id)

        if product_id not in {cart_product.id for cart_product in cart.products}:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=HTTPErrorMessagesEnum.PRODUCT_IS_NOT_ADDED_TO_THE_CART,
            )


class CartDeleteProductValidator(BaseCartValidator):
    """Cart delete product validator."""

    def __init__(
        self,
        request: Request,
        cart_service: CartService = Depends(),
        product_by_id_status_validator: ProductByIdStatusValidator = Depends(),
    ):
        """Initializes cart delete product validator.

        Args:
            request (Request): Current request object.
            cart_service (CartService): Cart service.
            product_by_id_status_validator (ProductByIdStatusValidator): Product
            by identifier status validator.

        """

        super().__init__(request=request, cart_service=cart_service)

        self.product_by_id_status_validator = product_by_id_status_validator

    async def validate(self, product_id: ObjectId) -> None:
        """Validates product on deleting it from the cart.

        Args:
            product_id (ObjectId): BSON object identifier of requested product.

        """

        await self.product_by_id_status_validator.validate(product_id=product_id)

        current_user = self.request.state.current_user

        cart = await self.cart_service.get_by_user_id(user_id=current_user.object.id)

        if product_id not in {cart_product.id for cart_product in cart.products}:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=HTTPErrorMessagesEnum.PRODUCT_IS_NOT_ADDED_TO_THE_CART,
            )
