"""Module that contains product service class."""


from typing import Any, List

import arrow
from bson import ObjectId
from fastapi import Depends

from app.api.v1.models import PaginationModel, SearchModel, SortingModel
from app.api.v1.models.product import CreateProductRequestModel, Product
from app.api.v1.repositories.product import ProductRepository
from app.api.v1.services import BaseService


class ProductService(BaseService):
    """Product service for encapsulating business logic."""

    def __init__(self, repository: ProductRepository = Depends()) -> None:
        """Initializes the product service.

        Args:
            repository (ProductRepository): An instance of the Product repository.

        """

        self.repository = repository

    async def get(
        self,
        filter_: Any,
        search: SearchModel,
        sorting: SortingModel,
        pagination: PaginationModel,
    ) -> List[Any]:
        """Retrieves a list of products based on parameters.

        Args:
            filter_ (Any): Parameters for list filtering.
            search (SearchModel): Parameters for list searching.
            sorting (SortingModel): Parameters for sorting.
            pagination (PaginationModel): Parameters for pagination.

        Returns:
            List[Any]: The retrieved list of products.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def count(self, filter_: Any, search: SearchModel) -> int:
        """Counts documents based on parameters.

        Args:
            filter_ (Any): Parameters for list filtering.
            search (SearchModel): Parameters for list searching.

        Returns:
            int: Count of documents.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

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
