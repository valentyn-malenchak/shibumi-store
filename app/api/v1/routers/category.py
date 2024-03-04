"""Module that contains category domain routers."""

from typing import Any, Dict, Mapping

from fastapi import APIRouter, Depends, Security, status

from app.api.v1.auth.auth import OptionalAuthorization
from app.api.v1.constants import ScopesEnum
from app.api.v1.dependencies.category import CategoryIdDependency
from app.api.v1.models.category import (
    CategoriesFilterModel,
    CategoriesListModel,
    Category,
    ExtendedCategoryResponseModel,
    ParametersValuesResponseModel,
)
from app.api.v1.models.user import CurrentUserModel
from app.api.v1.services.category import CategoryService

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=CategoriesListModel, status_code=status.HTTP_200_OK)
async def get_categories(
    _: CurrentUserModel | None = Security(
        OptionalAuthorization(), scopes=[ScopesEnum.CATEGORIES_GET_CATEGORIES.name]
    ),
    filter_: CategoriesFilterModel = Depends(),
    category_service: CategoryService = Depends(),
) -> Dict[str, Any]:
    """API which returns categories list.

    Args:
        _ (CurrentUserModel | None): Current user object or None.
        filter_ (CategoriesFilterModel): Parameters for list filtering.
        category_service (CategoryService): Category service.

    Returns:
        Dict[str, Any]: List of categories.

    """

    return dict(
        data=await category_service.get(filter_=filter_),
        total=await category_service.count(filter_=filter_),
    )


@router.get(
    "/{category_id}/",
    response_model=ExtendedCategoryResponseModel,
    status_code=status.HTTP_200_OK,
)
async def get_category(
    _: CurrentUserModel | None = Security(
        OptionalAuthorization(), scopes=[ScopesEnum.CATEGORIES_GET_CATEGORY.name]
    ),
    category: Category = Depends(CategoryIdDependency()),
) -> Category:
    """API which returns a specific category.

    Args:
        _ (CurrentUserModel | None): Current user object or None.
        category (Category): Category object.

    Returns:
        Category: Category object.

    """
    return category


@router.get(
    "/{category_id}/parameters-values/",
    response_model=ParametersValuesResponseModel | None,
    status_code=status.HTTP_200_OK,
)
async def get_product_parameters_values_by_category(
    _: CurrentUserModel | None = Security(
        OptionalAuthorization(),
        scopes=[ScopesEnum.CATEGORIES_GET_PARAMETERS_VALUES_BY_CATEGORY.name],
    ),
    category: Category = Depends(CategoryIdDependency()),
    category_service: CategoryService = Depends(),
) -> Mapping[str, Any] | None:
    """API which returns product parameters values by category identifier.

    Args:
        _ (CurrentUserModel | None): Current user object or None.
        category (Category): Category object.
        category_service (CategoryService): Category service.

    Returns:
         Mapping[str, Any] | None: Parameters values.

    """
    return await category_service.get_product_parameters_values_by_category(
        id_=category.id
    )
