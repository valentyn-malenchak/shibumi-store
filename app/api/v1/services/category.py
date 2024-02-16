"""Module that contains category service class."""


from typing import Any, List

from bson import ObjectId
from fastapi import Depends

from app.api.v1.models.category import CategoriesFilterModel, Category
from app.api.v1.repositories.category import CategoryRepository
from app.api.v1.services import BaseService


class CategoryService(BaseService):
    """Category service for encapsulating business logic."""

    def __init__(self, repository: CategoryRepository = Depends()) -> None:
        """Initializes the category service.

        Args:
            repository (CategoryRepository): An instance of the Category repository.

        """

        self.repository = repository

    async def get(
        self,
        filter_: CategoriesFilterModel,
        *_: Any,
    ) -> List[Any]:
        """Retrieves a list of categories based on parameters.

        Args:
            filter_ (CategoriesFilterModel): Parameters for list filtering.
            _ (Any): Parameters for list searching, sorting and pagination.

        Returns:
            List[Any]: The retrieved list of categories.

        """
        return await self.repository.get(path=filter_.path, leafs=filter_.leafs)

    async def count(self, filter_: CategoriesFilterModel, *_: Any) -> int:
        """Counts documents based on parameters.

        Args:
            filter_ (CategoriesFilterModel): Parameters for list filtering.
            _ (Any): Parameters for list searching.

        Returns:
            int: Count of documents.

        """
        return await self.repository.count(path=filter_.path, leafs=filter_.leafs)

    async def get_by_id(self, id_: ObjectId) -> Category | None:
        """Retrieves a category by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the category.

        Returns:
            Category | None: The retrieved category or None if not found.

        """

        category = await self.repository.get_by_id(id_=id_)

        return Category(**category) if category is not None else None

    async def create(self, item: Any) -> Any:
        """Creates a new category.

        Args:
            item (Any): The data for the new category.

        Returns:
            Any: The ID of created category.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def update_by_id(self, id_: ObjectId, item: Any) -> Any:
        """Updates a category by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the category.
            item (Any): Data to update category.

        Returns:
            Any: The updated category.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def delete_by_id(self, id_: ObjectId) -> None:
        """Deletes a category by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the category.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError
