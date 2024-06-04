"""Module that contains cart domain routers."""

from fastapi import APIRouter, Depends, Security, status

from app.api.v1.auth.auth import StrictAuthorization
from app.api.v1.constants import ScopesEnum
from app.api.v1.dependencies.cart import (
    CartProductAddDependency,
    CartProductDependency,
    CartProductUpdateDependency,
)
from app.api.v1.models.cart import Cart, CartProduct, CartResponseModel
from app.api.v1.models.user import CurrentUserModel
from app.api.v1.services.cart import CartService

router = APIRouter(prefix="/cart", tags=["cart"])


@router.get("/", response_model=CartResponseModel, status_code=status.HTTP_200_OK)
async def get_cart(
    current_user: CurrentUserModel = Security(
        StrictAuthorization(), scopes=[ScopesEnum.CARTS_GET_CART.name]
    ),
    cart_service: CartService = Depends(),
) -> Cart:
    """API which returns cart of current user.

    Args:
        current_user (CurrentUserModel): Current user object.
        cart_service (CartService): Cart service.

    Returns:
        Cart: Cart object.

    """
    return await cart_service.get_by_user_id(user_id=current_user.object.id)


@router.post("/", response_model=CartResponseModel, status_code=status.HTTP_201_CREATED)
async def add_product_to_the_cart(
    _: CurrentUserModel = Security(
        StrictAuthorization(), scopes=[ScopesEnum.CARTS_ADD_PRODUCT.name]
    ),
    cart_product: CartProduct = Depends(CartProductDependency()),
    cart: Cart = Depends(CartProductAddDependency()),
    cart_service: CartService = Depends(),
) -> Cart:
    """API which adds product to the cart.

    Args:
        _ (CurrentUserModel): Current user object.
        cart_product (CartProduct): Cart product to add.
        cart (Cart): Current user cart.
        cart_service (CartService): Cart service.

    Returns:
        Cart: Cart object.

    """
    return await cart_service.add_product_to_the_cart(item=cart, product=cart_product)


@router.patch("/", response_model=CartResponseModel, status_code=status.HTTP_200_OK)
async def update_product_in_the_cart(
    _: CurrentUserModel = Security(
        StrictAuthorization(), scopes=[ScopesEnum.CARTS_UPDATE_PRODUCT.name]
    ),
    cart_product: CartProduct = Depends(CartProductDependency()),
    cart: Cart = Depends(CartProductUpdateDependency()),
    cart_service: CartService = Depends(),
) -> Cart:
    """API which updates product in the cart.

    Args:
        _ (CurrentUserModel): Current user object.
        cart_product (CartProduct): Cart product to update.
        cart (Cart): Current user cart.
        cart_service (CartService): Cart service.

    Returns:
        Cart: Cart object.

    """
    return await cart_service.update_product_to_the_cart(
        item=cart, product=cart_product
    )
