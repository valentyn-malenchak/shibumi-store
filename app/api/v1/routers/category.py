"""Module that contains category domain routers."""

from typing import Any

from fastapi import APIRouter, Depends, Security, status

from app.api.v1.auth.auth import OptionalAuthorization
from app.api.v1.constants import ScopesEnum
from app.api.v1.dependencies.category import CategoryByIdDependency
from app.api.v1.models.category import (
    Category,
    CategoryFilter,
    CategoryList,
    CategoryParameters,
)
from app.api.v1.models.user import CurrentUser
from app.api.v1.services.category import CategoryService

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=CategoryList, status_code=status.HTTP_200_OK)
async def get_categories(
    _: CurrentUser | None = Security(
        OptionalAuthorization(), scopes=[ScopesEnum.CATEGORIES_GET_CATEGORIES.name]
    ),
    filter_: CategoryFilter = Depends(),
    category_service: CategoryService = Depends(),
) -> dict[str, Any]:
    """API which returns categories list.

    Args:
        _ (CurrentUser | None): Current user object or None.
        filter_ (CategoryFilter): Parameters for list filtering.
        category_service (CategoryService): Category service.

    Returns:
        dict[str, Any]: List of categories.

    """

    return dict(
        data=await category_service.get(filter_=filter_),
        total=await category_service.count(filter_=filter_),
    )


@router.get(
    "/{category_id}/",
    response_model=Category,
    status_code=status.HTTP_200_OK,
)
async def get_category(
    _: CurrentUser | None = Security(
        OptionalAuthorization(), scopes=[ScopesEnum.CATEGORIES_GET_CATEGORY.name]
    ),
    category: Category = Depends(CategoryByIdDependency()),
) -> Category:
    """API which returns a specific category.

    Args:
        _ (CurrentUser | None): Current user object or None.
        category (Category): Category object.

    Returns:
        Category: Category object.

    """
    return category


@router.get(
    "/{category_id}/parameters/",
    response_model=CategoryParameters | None,
    status_code=status.HTTP_200_OK,
)
async def get_category_parameters(
    _: CurrentUser | None = Security(
        OptionalAuthorization(),
        scopes=[ScopesEnum.CATEGORIES_GET_CATEGORY_PARAMETERS.name],
    ),
    category: Category = Depends(CategoryByIdDependency()),
    category_service: CategoryService = Depends(),
) -> CategoryParameters | None:
    """API which returns category parameters by its identifier.

    Args:
        _ (CurrentUser | None): Current user object or None.
        category (Category): Category object.
        category_service (CategoryService): Category service.

    Returns:
         CategoryParameters | None: Category parameters or None.

    """
    return await category_service.get_category_parameters(id_=category.id)
