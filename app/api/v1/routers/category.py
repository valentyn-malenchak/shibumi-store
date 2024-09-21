"""Module that contains category domain routers."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, Security, status

from app.api.v1.auth.auth import OptionalAuthorization
from app.api.v1.constants import ScopesEnum
from app.api.v1.dependencies.category import CategoryByIdGetDependency
from app.api.v1.models.category import (
    Category,
    CategoryFilter,
    CategoryList,
    CategoryParameters,
)
from app.api.v1.services.category import CategoryService

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get(
    "/",
    response_model=CategoryList,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Security(
            OptionalAuthorization(), scopes=[ScopesEnum.CATEGORIES_GET_CATEGORIES.name]
        )
    ],
)
async def get_categories(
    filter_: Annotated[CategoryFilter, Query()],
    category_service: CategoryService = Depends(),
) -> dict[str, Any]:
    """API which returns categories list.

    Args:
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
    dependencies=[
        Security(
            OptionalAuthorization(), scopes=[ScopesEnum.CATEGORIES_GET_CATEGORY.name]
        )
    ],
)
async def get_category(
    category: Category = Depends(CategoryByIdGetDependency()),
) -> Category:
    """API which returns a specific category.

    Args:
        category (Category): Category object.

    Returns:
        Category: Category object.

    """
    return category


@router.get(
    "/{category_id}/parameters/",
    response_model=CategoryParameters | None,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Security(
            OptionalAuthorization(),
            scopes=[ScopesEnum.CATEGORIES_GET_CATEGORY_PARAMETERS.name],
        )
    ],
)
async def get_category_parameters(
    category: Category = Depends(CategoryByIdGetDependency()),
    category_service: CategoryService = Depends(),
) -> CategoryParameters | None:
    """API which returns category parameters by its identifier.

    Args:
        category (Category): Category object.
        category_service (CategoryService): Category service.

    Returns:
         CategoryParameters | None: Category parameters or None.

    """
    return await category_service.get_category_parameters(id_=category.id)
