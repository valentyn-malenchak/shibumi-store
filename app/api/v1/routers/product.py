"""Module that contains product domain routers."""


from fastapi import APIRouter, Depends, Security, status

from app.api.v1.auth.auth import StrictAuthorization
from app.api.v1.constants import ScopesEnum
from app.api.v1.dependencies.product import CreateProductDependency
from app.api.v1.models.product import (
    CreateProductRequestModel,
    Product,
    ProductResponseModel,
)
from app.api.v1.models.user import CurrentUserModel
from app.api.v1.services.product import ProductService

router = APIRouter(prefix="/products", tags=["products"])


@router.post(
    "/", response_model=ProductResponseModel, status_code=status.HTTP_201_CREATED
)
async def create_product(
    _: CurrentUserModel = Security(
        StrictAuthorization(), scopes=[ScopesEnum.PRODUCTS_CREATE_PRODUCT.name]
    ),
    product_data: CreateProductRequestModel = Depends(CreateProductDependency()),
    product_service: ProductService = Depends(),
) -> Product | None:
    """API which creates a new product.

    Args:
        _ (CurrentUserModel): Current user object.
        product_data (CreateProductRequestModel): New product data.
        product_service (ProductService): Product service.

    Returns:
        Product | None: Created product object.

    """
    return await product_service.create(item=product_data)
