"""Module that contains category service class."""


from typing import Any, List, Mapping

from bson import ObjectId
from fastapi import BackgroundTasks, Depends

from app.api.v1.models.category import CategoriesFilterModel, Category
from app.api.v1.repositories.category import CategoryRepository
from app.api.v1.services import BaseService
from app.services.mongo.transaction_manager import TransactionManager
from app.services.redis.service import RedisService


class CategoryService(BaseService):
    """Category service for encapsulating business logic."""

    def __init__(
        self,
        background_tasks: BackgroundTasks,
        repository: CategoryRepository = Depends(),
        redis_service: RedisService = Depends(),
        transaction_manager: TransactionManager = Depends(),
    ) -> None:
        """Initializes the category service.

        Args:
            background_tasks (BackgroundTasks): Background tasks.
            repository (CategoryRepository): An instance of the Category repository.
            redis_service (RedisService): Redis service.
            transaction_manager (TransactionManager): Transaction manager.

        """

        super().__init__(
            background_tasks=background_tasks,
            redis_service=redis_service,
            transaction_manager=transaction_manager,
        )

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

    async def get_category_parameters(self, id_: ObjectId) -> Mapping[str, Any] | None:
        """Retrieves a category parameters by its identifier.

        Args:
            id_ (ObjectId): The unique identifier of the category.

        Returns:
             Mapping[str, Any] | None: The retrieved parameters or None if not found.

        """

        return await self.repository.get_category_parameters(id_=id_)

    async def calculate_category_parameters(self, id_: ObjectId) -> None:
        """Calculates list of parameters for specific product category.

        Args:
            id_ (ObjectId): The unique identifier of the category.

        """
        async with self.transaction_manager as session:
            await self.repository.calculate_category_parameters(
                id_=id_, session=session
            )
