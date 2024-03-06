"""Module that contains product service class."""


from typing import Any, List, Mapping

import arrow
from bson import ObjectId
from fastapi import BackgroundTasks, Depends

from app.api.v1.models import PaginationModel, SearchModel, SortingModel
from app.api.v1.models.product import (
    CreateProductRequestModel,
    Product,
    ProductsFilterModel,
)
from app.api.v1.repositories.product import ProductRepository
from app.api.v1.services import BaseService
from app.api.v1.services.category import CategoryService
from app.services.mongo.transaction_manager import TransactionManager
from app.services.redis.service import RedisService


class ProductService(BaseService):
    """Product service for encapsulating business logic."""

    def __init__(  # noqa: PLR0913
        self,
        background_tasks: BackgroundTasks,
        repository: ProductRepository = Depends(),
        redis_service: RedisService = Depends(),
        transaction_manager: TransactionManager = Depends(),
        category_service: CategoryService = Depends(),
    ) -> None:
        """Initializes the product service.

        Args:
            background_tasks (BackgroundTasks): Background tasks.
            repository (ProductRepository): An instance of the Product repository.
            redis_service (RedisService): Redis service.
            transaction_manager (TransactionManager): Transaction manager.
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
    ) -> List[Mapping[str, Any]]:
        """Retrieves a list of products based on parameters.

        Args:
            filter_ (ProductsFilterModel): Parameters for list filtering.
            search (SearchModel): Parameters for list searching.
            sorting (SortingModel): Parameters for sorting.
            pagination (PaginationModel): Parameters for pagination.

        Returns:
            List[Mapping[str, Any]]: The retrieved list of products.

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

    async def get_by_id(self, id_: ObjectId) -> Product | None:
        """Retrieves a product by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the product.

        Returns:
            Product | None: The retrieved product or None if not found.

        """

        product = await self.repository.get_by_id(id_=id_)

        return Product(**product) if product is not None else None

    async def create(self, item: CreateProductRequestModel) -> Product | None:
        """Creates a new product.

        Args:
            item (CreateProductRequestModel): The data for the new product.

        Returns:
            Product | None: The created product.

        """

        id_ = await self.repository.create(
            item={
                **item.model_dump(),
                "created_at": arrow.utcnow().datetime,
                "updated_at": None,
            },
        )

        self.background_tasks.add_task(
            self.category_service.calculate_category_parameters,
            id_=item.category_id,
        )

        return await self.get_by_id(id_=id_)

    async def update_by_id(self, id_: ObjectId, item: Any) -> Any:
        """Updates a product by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the product.
            item (Any): Data to update product.

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
