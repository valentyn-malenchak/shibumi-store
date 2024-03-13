"""Module that contains product domain routers."""


from typing import Any, Dict

from fastapi import APIRouter, Depends, Security, status

from app.api.v1.auth.auth import OptionalAuthorization, StrictAuthorization
from app.api.v1.constants import ScopesEnum
from app.api.v1.dependencies.product import (
    GetProductDependency,
    ProductDataDependency,
    ProductsFilterDependency,
)
from app.api.v1.models import PaginationModel, SearchModel, SortingModel
from app.api.v1.models.product import (
    ExtendedProductResponseModel,
    Product,
    ProductRequestModel,
    ProductsFilterModel,
    ProductsListModel,
)
from app.api.v1.models.user import CurrentUserModel
from app.api.v1.services.product import ProductService

router = APIRouter(prefix="/products", tags=["products"])


@router.post(
    "/",
    response_model=ExtendedProductResponseModel,
    status_code=status.HTTP_201_CREATED,
)
async def create_product(
    _: CurrentUserModel = Security(
        StrictAuthorization(), scopes=[ScopesEnum.PRODUCTS_CREATE_PRODUCT.name]
    ),
    product_data: ProductRequestModel = Depends(ProductDataDependency()),
    product_service: ProductService = Depends(),
) -> Product:
    """API which creates a new product.

    Args:
        _ (CurrentUserModel): Current user object.
        product_data (ProductRequestModel): New product data.
        product_service (ProductService): Product service.

    Returns:
        Product: Created product object.

    """
    return await product_service.create(data=product_data)


@router.get("/", response_model=ProductsListModel, status_code=status.HTTP_200_OK)
async def get_products(
    _: CurrentUserModel | None = Security(
        OptionalAuthorization(), scopes=[ScopesEnum.PRODUCTS_GET_PRODUCTS.name]
    ),
    filter_: ProductsFilterModel = Depends(ProductsFilterDependency()),
    search: SearchModel = Depends(),
    sorting: SortingModel = Depends(),
    pagination: PaginationModel = Depends(),
    product_service: ProductService = Depends(),
) -> Dict[str, Any]:
    """API which returns products list.

    Args:
        _ (CurrentUserModel | None): Current user object.
        filter_ (ProductsFilterModel): Parameters for list filtering.
        search (SearchModel): Parameters for list searching.
        sorting (SortingModel): Parameters for sorting.
        pagination (PaginationModel): Parameters for pagination.
        product_service (ProductService): Product service.

    Returns:
        ProductsListModel: List of products object.

    """

    return dict(
        data=await product_service.get(
            filter_=filter_, search=search, sorting=sorting, pagination=pagination
        ),
        total=await product_service.count(filter_=filter_, search=search),
    )


@router.get(
    "/{product_id}/",
    response_model=ExtendedProductResponseModel,
    status_code=status.HTTP_200_OK,
)
async def get_product(
    _: CurrentUserModel | None = Security(
        OptionalAuthorization(), scopes=[ScopesEnum.PRODUCTS_GET_PRODUCT.name]
    ),
    product: Product = Depends(GetProductDependency()),
    product_service: ProductService = Depends(),
) -> Product:
    """API which returns a specific product.

    Args:
        _ (CurrentUserModel | None): Current user object or None.
        product (Product): Product object.
        product_service (ProductService): Product service.

    Returns:
        Product: Product object.

    """

    await product_service.increment_views(id_=product.id)

    return product


@router.patch(
    "/{product_id}/",
    response_model=ExtendedProductResponseModel,
    status_code=status.HTTP_200_OK,
)
async def update_product(
    _: CurrentUserModel = Security(
        StrictAuthorization(), scopes=[ScopesEnum.PRODUCTS_UPDATE_PRODUCT.name]
    ),
    product: Product = Depends(GetProductDependency()),
    product_data: ProductRequestModel = Depends(ProductDataDependency()),
    product_service: ProductService = Depends(),
) -> Product:
    """API which updates a product.

    Args:
        _ (CurrentUserModel): Current user object.
        product (Product): Product object.
        product_data (ProductRequestModel): Product data to update.
        product_service (ProductService): Product service.

    Returns:
        Product: Updated product object.

    """
    return await product_service.update(item=product, data=product_data)
