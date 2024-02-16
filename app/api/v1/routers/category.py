"""Module that contains category domain routers."""

from typing import Any, Dict

from fastapi import APIRouter, Depends, Security, status

from app.api.v1.auth.auth import OptionalAuthorization
from app.api.v1.constants import ScopesEnum
from app.api.v1.dependencies.category import CategoryIdDependency
from app.api.v1.models.category import (
    CategoriesFilterModel,
    CategoriesListModel,
    Category,
    ExtendedCategoryResponseModel,
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
) -> Category | None:
    """API which returns a specific category.

    Args:
        _ (CurrentUserModel | None): Current user object or None.
        category (User): Category object.

    Returns:
        Category: Category object.

    """
    return category
