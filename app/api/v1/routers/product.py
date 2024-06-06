"""Module that contains product domain routers."""

from typing import Any

from fastapi import APIRouter, Depends, Security, status

from app.api.v1.auth.auth import OptionalAuthorization, StrictAuthorization
from app.api.v1.constants import ScopesEnum
from app.api.v1.dependencies.product import (
    ProductByIdStatusDependency,
    ProductDataDependency,
    ProductFilterDependency,
)
from app.api.v1.models import Pagination, Search, Sorting
from app.api.v1.models.product import (
    Product,
    ProductData,
    ProductFilter,
    ProductList,
)
from app.api.v1.models.user import CurrentUser
from app.api.v1.services.product import ProductService

router = APIRouter(prefix="/products", tags=["products"])


@router.post(
    "/",
    response_model=Product,
    status_code=status.HTTP_201_CREATED,
)
async def create_product(
    _: CurrentUser = Security(
        StrictAuthorization(), scopes=[ScopesEnum.PRODUCTS_CREATE_PRODUCT.name]
    ),
    product_data: ProductData = Depends(ProductDataDependency()),
    product_service: ProductService = Depends(),
) -> Product:
    """API which creates a new product.

    Args:
        _ (CurrentUser): Current user object.
        product_data (ProductData): New product data.
        product_service (ProductService): Product service.

    Returns:
        Product: Created product object.

    """
    return await product_service.create(data=product_data)


@router.get("/", response_model=ProductList, status_code=status.HTTP_200_OK)
async def get_products(
    _: CurrentUser | None = Security(
        OptionalAuthorization(), scopes=[ScopesEnum.PRODUCTS_GET_PRODUCTS.name]
    ),
    filter_: ProductFilter = Depends(ProductFilterDependency()),
    search: Search = Depends(),
    sorting: Sorting = Depends(),
    pagination: Pagination = Depends(),
    product_service: ProductService = Depends(),
) -> dict[str, Any]:
    """API which returns products list.

    Args:
        _ (CurrentUser | None): Current user object.
        filter_ (ProductFilter): Parameters for list filtering.
        search (Search): Parameters for list searching.
        sorting (Sorting): Parameters for sorting.
        pagination (Pagination): Parameters for pagination.
        product_service (ProductService): Product service.

    Returns:
        ProductList: List of products object.

    """

    return dict(
        data=await product_service.get(
            filter_=filter_, search=search, sorting=sorting, pagination=pagination
        ),
        total=await product_service.count(filter_=filter_, search=search),
    )


@router.get(
    "/{product_id}/",
    response_model=Product,
    status_code=status.HTTP_200_OK,
)
async def get_product(
    _: CurrentUser | None = Security(
        OptionalAuthorization(), scopes=[ScopesEnum.PRODUCTS_GET_PRODUCT.name]
    ),
    product: Product = Depends(ProductByIdStatusDependency()),
    product_service: ProductService = Depends(),
) -> Product:
    """API which returns a specific product.

    Args:
        _ (CurrentUser | None): Current user object or None.
        product (Product): Product object.
        product_service (ProductService): Product service.

    Returns:
        Product: Product object.

    """

    await product_service.increment_views(id_=product.id)

    return product


@router.patch(
    "/{product_id}/",
    response_model=Product,
    status_code=status.HTTP_200_OK,
)
async def update_product(
    _: CurrentUser = Security(
        StrictAuthorization(), scopes=[ScopesEnum.PRODUCTS_UPDATE_PRODUCT.name]
    ),
    product: Product = Depends(ProductByIdStatusDependency()),
    product_data: ProductData = Depends(ProductDataDependency()),
    product_service: ProductService = Depends(),
) -> Product:
    """API which updates a product.

    Args:
        _ (CurrentUser): Current user object.
        product (Product): Product object.
        product_data (ProductData): Product data to update.
        product_service (ProductService): Product service.

    Returns:
        Product: Updated product object.

    """
    return await product_service.update(item=product, data=product_data)
