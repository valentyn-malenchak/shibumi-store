"""Module that contains product service class."""

from collections.abc import Mapping
from typing import Any

import arrow
from bson import ObjectId
from fastapi import BackgroundTasks, Depends

from app.api.v1.models import PaginationModel, SearchModel, SortingModel
from app.api.v1.models.product import (
    Product,
    ProductRequestModel,
    ProductsFilterModel,
)
from app.api.v1.repositories.product import ProductRepository
from app.api.v1.services import BaseService
from app.api.v1.services.category import CategoryService
from app.exceptions import EntityIsNotFoundError
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
        category_service: CategoryService = Depends(),
    ) -> None:
        """Initializes the product service.

        Args:
            background_tasks (BackgroundTasks): Background tasks.
            redis_service (RedisService): Redis service.
            transaction_manager (TransactionManager): Transaction manager.
            repository (ProductRepository): An instance of the Product repository.
            category_service (CategoryService): Category service.

        """

        super().__init__(
            background_tasks=background_tasks,
            redis_service=redis_service,
            transaction_manager=transaction_manager,
        )

        self.repository = repository

        self.category_service = category_service

    async def get(
        self,
        filter_: ProductsFilterModel,
        search: SearchModel,
        sorting: SortingModel,
        pagination: PaginationModel,
    ) -> list[Mapping[str, Any]]:
        """Retrieves a list of products based on parameters.

        Args:
            filter_ (ProductsFilterModel): Parameters for list filtering.
            search (SearchModel): Parameters for list searching.
            sorting (SortingModel): Parameters for sorting.
            pagination (PaginationModel): Parameters for pagination.

        Returns:
            list[Mapping[str, Any]]: The retrieved list of products.

        """

        return await self.repository.get(
            search=search.search,
            sort_by=sorting.sort_by,
            sort_order=sorting.sort_order,
            page=pagination.page,
            page_size=pagination.page_size,
            category_id=filter_.category_id,
            available=filter_.available,
            parameters=filter_.parameters,
        )

    async def count(self, filter_: ProductsFilterModel, search: SearchModel) -> int:
        """Counts documents based on parameters.

        Args:
            filter_ (ProductsFilterModel): Parameters for list filtering.
            search (SearchModel): Parameters for list searching.

        Returns:
            int: Count of documents.

        """

        return await self.repository.count(
            search=search.search,
            category_id=filter_.category_id,
            available=filter_.available,
            parameters=filter_.parameters,
        )

    async def get_by_id(self, id_: ObjectId) -> Product:
        """Retrieves a product by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the product.

        Returns:
            Product: The retrieved product.

        Raises:
            EntityIsNotFoundError: If case product is not found.

        """

        product = await self.repository.get_by_id(id_=id_)

        if product is None:
            raise EntityIsNotFoundError

        return Product(**product)

    async def increment_views(self, id_: ObjectId) -> None:
        """Increments a views field for product by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the product.

        """
        self.background_tasks.add_task(self.repository.increment_views, id_=id_)

    async def create(self, data: ProductRequestModel) -> Product:
        """Creates a new product.

        Args:
            data (ProductRequestModel): The data for the new product.

        Returns:
            Product: The created product.

        """

        id_ = await self.repository.create(
            data={
                **data.model_dump(),
                "views": 0,
                "created_at": arrow.utcnow().datetime,
                "updated_at": None,
            },
        )

        self.background_tasks.add_task(
            self.category_service.calculate_category_parameters,
            id_=data.category_id,
        )

        return await self.get_by_id(id_=id_)

    async def update(self, item: Product, data: ProductRequestModel) -> Product:
        """Updates a product object.

        Args:
            item (Product): Product object.
            data (ProductRequestModel): Data to update product.

        Returns:
            Product: The updated product.

        """

        await self.repository.update_by_id(
            id_=item.id,
            data={
                **data.model_dump(),
                "updated_at": arrow.utcnow().datetime,
            },
        )

        self.background_tasks.add_task(
            self.category_service.calculate_category_parameters,
            id_=data.category_id,
        )

        # Recalculate parameters for "old" category, if category field is updated
        if item.category_id != data.category_id:
            self.background_tasks.add_task(
                self.category_service.calculate_category_parameters,
                id_=item.category_id,
            )

        return await self.get_by_id(id_=item.id)

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
