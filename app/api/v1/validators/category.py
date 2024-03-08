"""Contains category domain validators."""


from typing import Any

from bson import ObjectId
from fastapi import Depends, HTTPException, Request, status

from app.api.v1.models.category import Category
from app.api.v1.services.category import CategoryService
from app.api.v1.validators import BaseValidator
from app.constants import HTTPErrorMessagesEnum
from app.exceptions import EntityIsNotFoundError


class BaseCategoryValidator(BaseValidator):
    """Base category validator."""

    def __init__(self, request: Request, category_service: CategoryService = Depends()):
        """Initializes base category validator.

        Args:
            request (Request): Current request object.
            category_service (UserService): Category service.

        """

        super().__init__(request=request)

        self.category_service = category_service

    async def validate(self, *args: Any) -> Any:
        """Validates data.

        Args:
            args (Any): Method arguments.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.

        """
        raise NotImplementedError


class CategoryIdValidator(BaseCategoryValidator):
    """Category identifier validator."""

    async def validate(self, category_id: ObjectId) -> Category:
        """Validates requested category by id.

        Args:
            category_id (ObjectId): BSON object identifier of requested category.

        Returns:
            Category: Category object.

        Raises:
            HTTPException: If requested category is not found.

        """

        try:
            category = await self.category_service.get_by_id(id_=category_id)

        except EntityIsNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=HTTPErrorMessagesEnum.ENTITY_IS_NOT_FOUND.format(  # type: ignore
                    entity="Category"
                ),
            )

        return category


class LeafCategoryValidator(BaseCategoryValidator):
    """Leaf category validator."""

    def __init__(
        self,
        request: Request,
        category_service: CategoryService = Depends(),
        category_id_validator: CategoryIdValidator = Depends(),
    ):
        """Initializes base category validator.

        Args:
            request (Request): Current request object.
            category_service (UserService): Category service.
            category_id_validator (CategoryIdValidator): Category identifier validator.

        """

        super().__init__(request=request, category_service=category_service)

        self.category_id_validator = category_id_validator

    async def validate(self, category_id: ObjectId) -> Category:
        """Validates requested category by id.

        Args:
            category_id (ObjectId): BSON object identifier of requested category.

        Returns:
            Category: Category object.

        Raises:
            HTTPException: If requested category is not a leaf of tree.

        """

        category = await self.category_id_validator.validate(category_id=category_id)

        if category.has_children is True:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=HTTPErrorMessagesEnum.LEAF_PRODUCT_CATEGORY_REQUIRED,
            )

        return category
