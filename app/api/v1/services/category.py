"""Module that contains category service class."""

from collections.abc import Mapping
from typing import Any

from bson import ObjectId
from fastapi import BackgroundTasks, Depends

from app.api.v1.models.category import Category, CategoryFilter
from app.api.v1.repositories.category import CategoryRepository
from app.api.v1.services import BaseService
from app.exceptions import EntityIsNotFoundError
from app.services.mongo.transaction_manager import TransactionManager
from app.services.redis.service import RedisService


class CategoryService(BaseService):
    """Category service for encapsulating business logic."""

    def __init__(
        self,
        background_tasks: BackgroundTasks,
        redis_service: RedisService = Depends(),
        transaction_manager: TransactionManager = Depends(),
        repository: CategoryRepository = Depends(),
    ) -> None:
        """Initializes the category service.

        Args:
            background_tasks (BackgroundTasks): Background tasks.
            redis_service (RedisService): Redis service.
            transaction_manager (TransactionManager): Transaction manager.
            repository (CategoryRepository): An instance of the Category repository.

        """

        super().__init__(
            background_tasks=background_tasks,
            redis_service=redis_service,
            transaction_manager=transaction_manager,
        )

        self.repository = repository

    async def get(
        self,
        filter_: CategoryFilter,
        *_: Any,
    ) -> list[Any]:
        """Retrieves a list of categories based on parameters.

        Args:
            filter_ (CategoryFilter): Parameters for list filtering.
            _ (Any): Parameters for list searching, sorting and pagination.

        Returns:
            list[Any]: The retrieved list of categories.

        """
        return await self.repository.get(
            search=None,
            page=None,
            page_size=None,
            sort_by=None,
            sort_order=None,
            path=filter_.path,
            leafs=filter_.leafs,
        )

    async def count(self, filter_: CategoryFilter, *_: Any) -> int:
        """Counts categories based on parameters.

        Args:
            filter_ (CategoryFilter): Parameters for list filtering.
            _ (Any): Parameters for list searching.

        Returns:
            int: Count of categories.

        """
        return await self.repository.count(
            search=None, path=filter_.path, leafs=filter_.leafs
        )

    async def get_by_id(self, id_: ObjectId) -> Category:
        """Retrieves a category by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the category.

        Returns:
            Category: The retrieved category.

        """

        category = await self.repository.get_by_id(id_=id_)

        return Category(**category)

    async def create_raw(self, data: Any) -> Any:
        """Creates a raw new category.

        Args:
            data (Any): The data for the new category.

        Returns:
            Any: The ID of created category.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def create(self, data: Any) -> Any:
        """Creates a new category.

        Args:
            data (Any): The data for the new category.

        Returns:
            Any: Created category.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def update(self, item: Any, data: Any) -> Any:
        """Updates a category object.

        Args:
            item (Any): Category object.
            data (Any): Data to update category.

        Returns:
            Any: The updated category.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def update_by_id(self, id_: ObjectId, data: Any) -> Any:
        """Updates a category by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the category.
            data (Any): Data to update category.

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

    async def delete(self, item: Any) -> None:
        """Deletes a category.

        Args:
            item (Any): Category object.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def get_category_parameters(self, id_: ObjectId) -> Mapping[str, Any] | None:
        """Retrieves a category parameters by its identifier.

        Args:
            id_ (ObjectId): The unique identifier of the category.

        Returns:
             Mapping[str, Any] | None: The retrieved parameters or None if not found.

        """

        try:
            return await self.repository.get_category_parameters(id_=id_)
        except EntityIsNotFoundError:
            return None

    async def calculate_category_parameters(self, id_: ObjectId) -> None:
        """Calculates list of parameters for specific product category.

        Args:
            id_ (ObjectId): The unique identifier of the category.

        """
        async with self.transaction_manager as session:
            await self.repository.calculate_category_parameters(
                id_=id_, session=session
            )
