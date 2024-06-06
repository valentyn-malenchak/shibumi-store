"""Contains category domain dependencies."""

from typing import Annotated

from bson import ObjectId
from fastapi import Depends

from app.api.v1.models.category import Category
from app.api.v1.validators.category import CategoryByIdValidator
from app.utils.pydantic import ObjectIdAnnotation


class CategoryByIdDependency:
    """Category by identifier dependency."""

    async def __call__(
        self,
        category_id: Annotated[ObjectId, ObjectIdAnnotation],
        category_by_id_validator: CategoryByIdValidator = Depends(),
    ) -> Category:
        """Checks category from request by identifier.

        Args:
            category_id (Annotated[ObjectId, ObjectIdAnnotation]): BSON object
            identifier of requested category.
            category_by_id_validator (CategoryByIdValidator): Category by identifier
            validator.

        Returns:
            Category: Category object.

        """

        return await category_by_id_validator.validate(category_id=category_id)
