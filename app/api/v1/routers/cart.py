"""Module that contains cart domain routers."""

from typing import Annotated

from bson import ObjectId
from fastapi import APIRouter, Depends, Security, status

from app.api.v1.auth.auth import StrictAuthorization
from app.api.v1.constants import ScopesEnum
from app.api.v1.dependencies.cart import (
    CartProductAddDependency,
    CartProductDeleteDependency,
    CartProductUpdateDependency,
)
from app.api.v1.models.cart import (
    Cart,
    CartProduct,
    CartProductQuantity,
)
from app.api.v1.models.user import CurrentUser
from app.api.v1.services.cart import CartService
from app.utils.pydantic import ObjectIdAnnotation

router = APIRouter(prefix="/cart", tags=["cart"])


@router.get("/", response_model=Cart, status_code=status.HTTP_200_OK)
async def get_cart(
    current_user: CurrentUser = Security(
        StrictAuthorization(), scopes=[ScopesEnum.CARTS_GET_CART.name]
    ),
    cart_service: CartService = Depends(),
) -> Cart:
    """API which returns cart of current user.

    Args:
        current_user (CurrentUser): Current user object.
        cart_service (CartService): Cart service.

    Returns:
        Cart: Cart object.

    """
    return await cart_service.get_by_user_id(user_id=current_user.object.id)


@router.post("/", response_model=Cart, status_code=status.HTTP_201_CREATED)
async def add_product_to_the_cart(
    current_user: CurrentUser = Security(
        StrictAuthorization(), scopes=[ScopesEnum.CARTS_ADD_PRODUCT.name]
    ),
    cart_product: CartProduct = Depends(CartProductAddDependency()),
    cart_service: CartService = Depends(),
) -> Cart:
    """API which adds product to the cart.

    Args:
        current_user (CurrentUser): Current user object.
        cart_product (CartProduct): Cart product data.
        cart_service (CartService): Cart service.

    Returns:
        Cart: Cart object.

    """
    return await cart_service.add_product(
        user_id=current_user.object.id, data=cart_product
    )


@router.patch("/{product_id}/", response_model=Cart, status_code=status.HTTP_200_OK)
async def update_product_in_the_cart(
    product_id: Annotated[ObjectId, ObjectIdAnnotation],
    current_user: CurrentUser = Security(
        StrictAuthorization(), scopes=[ScopesEnum.CARTS_UPDATE_PRODUCT.name]
    ),
    cart_product_quantity: CartProductQuantity = Depends(CartProductUpdateDependency()),
    cart_service: CartService = Depends(),
) -> Cart:
    """API which updates product in the cart.

    Args:
        product_id (Annotated[ObjectId, ObjectIdAnnotation]): BSON object
        identifier of requested product.
        current_user (CurrentUser): Current user object.
        cart_product_quantity (CartProductQuantity): Cart product quantity data.
        cart_service (CartService): Cart service.

    Returns:
        Cart: Cart object.

    """
    return await cart_service.update_product(
        user_id=current_user.object.id,
        product_id=product_id,
        data=cart_product_quantity,
    )


@router.delete("/{product_id}/", response_model=Cart, status_code=status.HTTP_200_OK)
async def delete_product_from_the_cart(
    current_user: CurrentUser = Security(
        StrictAuthorization(), scopes=[ScopesEnum.CARTS_DELETE_PRODUCT.name]
    ),
    product_id: ObjectId = Depends(CartProductDeleteDependency()),
    cart_service: CartService = Depends(),
) -> Cart:
    """API which deletes product from the cart.

    Args:
        current_user (CurrentUser): Current user object.
        product_id (ObjectId): BSON object identifier of requested product.
        cart_service (CartService): Cart service.

    """
    return await cart_service.delete_product(
        user_id=current_user.object.id,
        product_id=product_id,
    )
