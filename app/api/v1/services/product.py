"""Module that contains product service class."""

from collections.abc import Mapping
from typing import Any

from bson import ObjectId
from fastapi import BackgroundTasks, Depends

from app.api.v1.models import Pagination, Search, Sorting
from app.api.v1.models.product import (
    Product,
    ProductData,
    ProductFilter,
)
from app.api.v1.models.thread import ThreadCreateData
from app.api.v1.repositories.product import ProductRepository
from app.api.v1.services import BaseService
from app.api.v1.services.category import CategoryService
from app.api.v1.services.thread import ThreadService
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
        thread_service: ThreadService = Depends(),
    ) -> None:
        """Initializes the product service.

        Args:
            background_tasks (BackgroundTasks): Background tasks.
            redis_service (RedisService): Redis service.
            transaction_manager (TransactionManager): Transaction manager.
            repository (ProductRepository): An instance of the Product repository.
            category_service (CategoryService): Category service.
            thread_service (ThreadService): Thread service.

        """

        super().__init__(
            background_tasks=background_tasks,
            redis_service=redis_service,
            transaction_manager=transaction_manager,
        )

        self.repository = repository

        self.category_service = category_service

        self.thread_service = thread_service

    async def get(
        self,
        filter_: ProductFilter,
        search: Search,
        sorting: Sorting,
        pagination: Pagination,
    ) -> list[Mapping[str, Any]]:
        """Retrieves a list of products based on parameters.

        Args:
            filter_ (ProductFilter): Parameters for list filtering.
            search (Search): Parameters for list searching.
            sorting (Sorting): Parameters for sorting.
            pagination (Pagination): Parameters for pagination.

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
            ids=filter_.ids,
            parameters=filter_.parameters,
        )

    async def count(self, filter_: ProductFilter, search: Search) -> int:
        """Counts products based on parameters.

        Args:
            filter_ (ProductFilter): Parameters for list filtering.
            search (Search): Parameters for list searching.

        Returns:
            int: Count of products.

        """

        return await self.repository.count(
            search=search.search,
            category_id=filter_.category_id,
            available=filter_.available,
            ids=filter_.ids,
            parameters=filter_.parameters,
        )

    async def get_by_id(self, id_: ObjectId) -> Product:
        """Retrieves a product by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the product.

        Returns:
            Product: The retrieved product.

        """

        product = await self.repository.get_by_id(id_=id_)

        return Product(**product)

    async def create_raw(self, data: ProductData) -> Any:
        """Creates a raw new product.

        Args:
            data (ProductData): The data for the new product.

        Returns:
            Any: The ID of created product.

        """

        # Initialize product thread
        thread = await self.thread_service.create(
            data=ThreadCreateData(name=data.name, body=data.synopsis)
        )

        return await self.repository.create(
            name=data.name,
            synopsis=data.synopsis,
            description=data.description,
            quantity=data.quantity,
            price=data.price,
            category_id=data.category_id,
            available=data.available,
            html_body=data.html_body,
            parameters=data.parameters,
            thread_id=thread.id,
        )

    async def create(self, data: ProductData) -> Product:
        """Creates a new product.

        Args:
            data (ProductData): The data for the new product.

        Returns:
            Product: Created product.

        """

        id_ = await self.create_raw(data=data)

        self.background_tasks.add_task(
            self.category_service.calculate_category_parameters,
            id_=data.category_id,
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

        updated_product = await self.repository.get_and_update_by_id(
            id_=item.id,
            name=data.name,
            synopsis=data.synopsis,
            description=data.description,
            quantity=data.quantity,
            price=data.price,
            category_id=data.category_id,
            available=data.available,
            html_body=data.html_body,
            parameters=data.parameters,
        )

        product = Product(**updated_product)

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
