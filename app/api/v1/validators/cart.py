"""Contains cart domain validators."""

from typing import Any

from bson import ObjectId
from fastapi import Depends, HTTPException, Request, status

from app.api.v1.models.cart import Cart
from app.api.v1.services.cart import CartService
from app.api.v1.validators import BaseValidator
from app.constants import HTTPErrorMessagesEnum
from app.exceptions import EntityIsNotFoundError


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


class CartByIdValidator(BaseCartValidator):
    """Cart by identifier validator."""

    async def validate(self, cart_id: ObjectId) -> Cart:
        """Validates requested cart by identifier.

        Args:
            cart_id (ObjectId): BSON object identifier of requested cart.

        Returns:
            Cart: Cart object.

        Raises:
            HTTPException: If requested cart is not found.

        """

        try:
            cart = await self.cart_service.get_by_id(id_=cart_id)

        except EntityIsNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=HTTPErrorMessagesEnum.ENTITY_IS_NOT_FOUND.format(entity="Cart"),
            )

        return cart


class CartAccessValidator(BaseCartValidator):
    """Cart access validator."""

    async def validate(self, cart: Cart) -> Cart:
        """Validates access to cart.

        Args:
            cart (Cart): Cart object.

        Returns:
            Cart: Cart object.

        Raises:
            HTTPException: If user requests cart of another user.

        """

        current_user = self.request.state.current_user

        if cart.user_id != current_user.object.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=HTTPErrorMessagesEnum.ACCESS_DENIED.format(destination="cart"),
            )

        return cart


class CartByUserValidator(BaseCartValidator):
    """Cart by user validator."""

    async def validate(self) -> Cart:
        """Validates requested cart by user.

        Returns:
            Cart: Cart object.

        Raises:
            HTTPException: If requested user cart is not found.

        """

        current_user = self.request.state.current_user

        try:
            cart = await self.cart_service.get_by_user_id(
                user_id=current_user.object.id
            )

        except EntityIsNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=HTTPErrorMessagesEnum.ENTITY_IS_NOT_FOUND.format(entity="Cart"),
            )

        return cart


class CartProductValidator(BaseCartValidator):
    """Cart product validator."""

    async def validate(
        self, product_id: ObjectId, cart: Cart, negative: bool = False
    ) -> None:
        """Validates if product is added to cart or opposite.

        Args:
            product_id (ObjectId): BSON object identifier of requested product.
            cart (Cart): Cart object.
            negative (bool): If True, validates the product shouldn't be in cart,
            otherwise, validates the product should be present in the cart.
            Defaults to False.

        """

        cart_products = {cart_product.id for cart_product in cart.products}

        # in case product should be in cart, but it is not
        if negative is False and product_id not in cart_products:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=HTTPErrorMessagesEnum.PRODUCT_IS_NOT_ADDED_TO_THE_CART,
            )

        # in case product shouldn't be in cart, but it is
        elif negative is True and product_id in cart_products:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=HTTPErrorMessagesEnum.PRODUCT_IS_ALREADY_ADDED_TO_THE_CART,
            )
