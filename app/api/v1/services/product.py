"""Module that contains product service class."""

from collections.abc import Mapping
from typing import Any

from bson import ObjectId
from fastapi import BackgroundTasks, Depends

from app.api.v1.models import Pagination, Search, Sorting
from app.api.v1.models.product import (
    Product,
    ProductCreateData,
    ProductData,
    ProductFilter,
)
from app.api.v1.models.thread import ThreadData
from app.api.v1.repositories.category import CategoryRepository
from app.api.v1.repositories.category_parameters import CategoryParametersRepository
from app.api.v1.repositories.product import ProductRepository
from app.api.v1.repositories.thread import ThreadRepository
from app.api.v1.services import BaseService
from app.services.mongo.transaction_manager import TransactionManager
from app.services.redis.service import RedisService


class ProductService(BaseService):
    """Product service for encapsulating business logic."""

    def __init__(  # noqa: PLR0913
        self,
        background_tasks: BackgroundTasks,
        redis_service: RedisService = Depends(),
        transaction_manager: TransactionManager = Depends(),
        repository: ProductRepository = Depends(),
        category_repository: CategoryRepository = Depends(),
        category_parameters_repository: CategoryParametersRepository = Depends(),
        thread_repository: ThreadRepository = Depends(),
    ) -> None:
        """Initializes the product service.

        Args:
            background_tasks (BackgroundTasks): Background tasks.
            redis_service (RedisService): Redis service.
            transaction_manager (TransactionManager): Transaction manager.
            repository (ProductRepository): An instance of the Product repository.
            category_repository (CategoryRepository): An instance of the category
            repository.
            category_parameters_repository (CategoryParametersRepository): An instance
            of the category-parameters repository.
            thread_repository (ThreadRepository): An instance of the thread repository.

        """

        super().__init__(
            background_tasks=background_tasks,
            redis_service=redis_service,
            transaction_manager=transaction_manager,
        )

        self.repository = repository

        self.category_repository = category_repository

        self.category_parameters_repository = category_parameters_repository

        self.thread_repository = thread_repository

    async def get(
        self,
        *,
        filter_: ProductFilter | None = None,
        search: Search | None = None,
        sorting: Sorting | None = None,
        pagination: Pagination | None = None,
        **kwargs: Any,
    ) -> list[Mapping[str, Any]]:
        """Retrieves a list of products based on parameters.

        Args:
            filter_ (ProductFilter | None): Parameters for list filtering.
            Defaults to None.
            search (Search | None): Parameters for list searching. Defaults to None.
            sorting (Sorting | None): Parameters for sorting. Defaults to None.
            pagination (Pagination | None): Parameters for pagination. Defaults to None.
            kwargs (Any): Keyword arguments.

        Returns:
            list[Mapping[str, Any]]: The retrieved list of products.

        """
        return await self.repository.get(
            filter_=filter_,
            search=search,
            sorting=sorting,
            pagination=pagination,
        )

    async def count(
        self,
        *,
        filter_: ProductFilter | None = None,
        search: Search | None = None,
        **kwargs: Any,
    ) -> int:
        """Counts products based on parameters.

        Args:
            filter_ (ProductFilter | None): Parameters for list filtering.
            Defaults to None.
            search (Search | None): Parameters for list searching. Defaults to None.
            kwargs (Any): Keyword arguments.

        Returns:
            int: Count of products.

        """
        return await self.repository.count(
            filter_=filter_,
            search=search,
        )

    async def get_by_id(self, id_: ObjectId) -> Product:
        """Retrieves a product by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the product.

        Returns:
            Product: The retrieved product.

        """
        return await self.repository.get_by_id(id_=id_)

    async def create(self, data: ProductData) -> Product:
        """Creates a new product.

        Args:
            data (ProductData): The data for the new product.

        Returns:
            Product: Created product.

        """

        # Initialize product thread
        thread_id = await self.thread_repository.create(
            data=ThreadData(name=data.name, body=data.synopsis)
        )

        id_ = await self.repository.create(
            data=ProductCreateData(**data.model_dump(), thread_id=thread_id)
        )

        self.background_tasks.add_task(
            self.calculate_category_parameters,
            category_id=data.category_id,
        )

        return await self.get_by_id(id_=id_)

    async def update(self, item: Product, data: ProductData) -> Product:
        """Updates a product object.

        Args:
            item (Product): Product object.
            data (ProductData): Data to update product.

        Returns:
            Product: The updated product.

        """

        product = await self.repository.get_and_update_by_id(id_=item.id, data=data)

        self.background_tasks.add_task(
            self.calculate_category_parameters,
            category_id=data.category_id,
        )

        # Recalculate parameters for "old" category, if category field is updated
        if item.category_id != data.category_id:
            self.background_tasks.add_task(
                self.calculate_category_parameters,
                category_id=item.category_id,
            )

        return product

    async def update_by_id(self, id_: ObjectId, data: Any) -> Any:
        """Updates a product by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the product.
            data (Any): Data to update product.

        Returns:
            Any: The updated product.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def delete_by_id(self, id_: ObjectId) -> None:
        """Deletes a product by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the product.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def delete(self, item: Any) -> None:
        """Deletes a product.

        Args:
            item (Any): Product object.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def increment_views(self, id_: ObjectId) -> None:
        """Increments a views field for product by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the product.

        """
        self.background_tasks.add_task(self.repository.increment_views, id_=id_)

    async def calculate_category_parameters(self, category_id: ObjectId) -> None:
        """Calculates and stores list of parameters for specific product category.

        Args:
            category_id (ObjectId): The unique identifier of the category.

        """

        async with self.transaction_manager as session:
            category_parameters = (
                await self.category_repository.calculate_category_parameters(
                    id_=category_id, session=session
                )
            )

            await self.category_parameters_repository.update_by_id(
                id_=category_parameters["_id"],
                data=category_parameters,
                upsert=True,
                session=session,
            )
