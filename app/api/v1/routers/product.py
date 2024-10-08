"""Module that contains product domain routers."""

from typing import Any

from fastapi import APIRouter, Depends, Security, status

from app.api.v1.constants import ScopesEnum
from app.api.v1.dependencies.auth import (
    OptionalAuthorizationDependency,
    StrictAuthorizationDependency,
)
from app.api.v1.dependencies.product import (
    ProductAccessDependency,
    ProductDataDependency,
    ProductsFilterDependency,
)
from app.api.v1.models import Pagination, Search, Sorting
from app.api.v1.models.product import (
    Product,
    ProductData,
    ProductFilter,
    ProductList,
)
from app.api.v1.services.product import ProductService

router = APIRouter(prefix="/products", tags=["products"])


@router.post(
    "/",
    response_model=Product,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Security(
            StrictAuthorizationDependency(),
            scopes=[ScopesEnum.PRODUCTS_CREATE_PRODUCT.name],
        )
    ],
)
async def create_product(
    product_data: ProductData = Depends(ProductDataDependency()),
    product_service: ProductService = Depends(),
) -> Product:
    """API which creates a new product.

    Args:
        product_data (ProductData): New product data.
        product_service (ProductService): Product service.

    Returns:
        Product: Created product object.

    """
    return await product_service.create(data=product_data)


@router.get(
    "/",
    response_model=ProductList,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Security(
            OptionalAuthorizationDependency(),
            scopes=[ScopesEnum.PRODUCTS_GET_PRODUCTS.name],
        )
    ],
)
async def get_products(
    filter_: ProductFilter = Depends(ProductsFilterDependency()),
    search: Search = Depends(),
    sorting: Sorting = Depends(),
    pagination: Pagination = Depends(),
    product_service: ProductService = Depends(),
) -> dict[str, Any]:
    """API which returns products list.

    Args:
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
    dependencies=[
        Security(
            OptionalAuthorizationDependency(),
            scopes=[ScopesEnum.PRODUCTS_GET_PRODUCT.name],
        )
    ],
)
async def get_product(
    product: Product = Depends(ProductAccessDependency()),
    product_service: ProductService = Depends(),
) -> Product:
    """API which returns a specific product.

    Args:
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
    dependencies=[
        Security(
            StrictAuthorizationDependency(),
            scopes=[ScopesEnum.PRODUCTS_UPDATE_PRODUCT.name],
        )
    ],
)
async def update_product(
    product_data: ProductData = Depends(ProductDataDependency()),
    product: Product = Depends(ProductAccessDependency()),
    product_service: ProductService = Depends(),
) -> Product:
    """API which updates a product.

    Args:
        product_data (ProductData): Product data to update.
        product (Product): Product object.
        product_service (ProductService): Product service.

    Returns:
        Product: Updated product object.

    """
    return await product_service.update(item=product, data=product_data)
