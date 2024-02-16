"""Contains category domain dependencies."""

from typing import Annotated

from bson import ObjectId
from fastapi import Depends

from app.api.v1.models import ObjectIdAnnotation
from app.api.v1.models.category import Category
from app.api.v1.validators.category import CategoryIdValidator


class CategoryIdDependency:
    """Category identifier dependency."""

    async def __call__(
        self,
        category_id: Annotated[ObjectId, ObjectIdAnnotation],
        category_id_validator: CategoryIdValidator = Depends(),
    ) -> Category:
        """Checks category from request by identifier.

        Args:
            category_id (Annotated[ObjectId, ObjectIdAnnotation]): BSON object
            identifier of requested category.
            category_id_validator (CategoryIdValidator): Category identifier validator.

        Returns:
            Category: Category object.

        """

        return await category_id_validator.validate(category_id=category_id)
