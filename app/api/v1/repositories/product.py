"""Module that contains product repository class."""

from collections.abc import Mapping
from typing import Any

import arrow
from bson import ObjectId
from injector import inject
from motor.motor_asyncio import AsyncIOMotorClientSession

from app.api.v1.models import Search
from app.api.v1.models.product import (
    Product,
    ProductCreateData,
    ProductData,
    ProductFilter,
)
from app.api.v1.repositories import BaseRepository
from app.constants import ProjectionValuesEnum, SortingValuesEnum
from app.services.mongo.constants import MongoCollectionsEnum


@inject
class ProductRepository(BaseRepository):
    """Product repository for handling data access operations."""

    _collection_name: str = MongoCollectionsEnum.PRODUCTS

    async def _get_list_query_filter(
        self, filter_: ProductFilter, search: Search | None
    ) -> Mapping[str, Any]:
        """Returns a query filter for list of products.

        Args:
            filter_ (ProductFilter): Parameters for list filtering.
            search (Search | None): Parameters for list searching.

        Returns:
            (Mapping[str, Any]): List query filter.

        """

        query_filter: dict[str, Any] = {}

        self._apply_list_search(query_filter=query_filter, search=search)

        if filter_.category_id is not None:
            query_filter["category_id"] = filter_.category_id

        if filter_.available is not None:
            query_filter["available"] = filter_.available

        if filter_.ids:
            query_filter["_id"] = {"$in": filter_.ids}

        if filter_.parameters:
            for name, values in filter_.parameters.items():
                query_filter[f"parameters.{name}"] = (
                    values[0] if len(values) == 1 else {"$in": values}
                )

        return query_filter

    @staticmethod
    def _get_list_query_projection() -> Mapping[str, Any] | None:
        """Returns a query projection for list of products.

        Returns:
            Mapping[str, Any] | None: List query projection or None.

        """

        return {
            "description": ProjectionValuesEnum.EXCLUDE,
            "html_body": ProjectionValuesEnum.EXCLUDE,
            "parameters": ProjectionValuesEnum.EXCLUDE,
        }

    @staticmethod
    def _get_list_default_sorting() -> list[tuple[str, int | Mapping[str, Any]]] | None:
        """Returns default sorting for list of products.

        Returns:
            list[tuple[str, int | Mapping[str, Any]]] | None: Default sorting.

        """
        return [("views", SortingValuesEnum.DESC)]

    async def get_by_id(
        self, id_: ObjectId, *, session: AsyncIOMotorClientSession | None = None
    ) -> Product:
        """Retrieves a product from the repository by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the product.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            Product: The retrieved product object.

        """

        product = await self._get_one(_id=id_, session=session)

        return Product(**product)

    async def get_and_update_by_id(
        self,
        id_: ObjectId,
        data: ProductData,
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> Product:
        """
        Updates and retrieves a single product from the repository by its
        unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the product.
            data (ProductData): Data to update product.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            Product: The retrieved product object.

        """

        product = await self._mongo_service.find_one_and_update(
            collection=self._collection_name,
            filter_={"_id": id_},
            update={
                "$set": {
                    "name": data.name,
                    "synopsis": data.synopsis,
                    "description": data.description,
                    "quantity": data.quantity,
                    "price": data.price,
                    "category_id": data.category_id,
                    "available": data.available,
                    "html_body": data.html_body,
                    "parameters": data.parameters,
                    "updated_at": arrow.utcnow().datetime,
                }
            },
            session=session,
        )

        return Product(**product)

    async def create(
        self,
        data: ProductCreateData,
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> Any:
        """Creates a new product in repository.

        Args:
            data (ProductCreateData): The data for the new product.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            Any: The ID of created product.

        """

        return await self._mongo_service.insert_one(
            collection=self._collection_name,
            document={
                "name": data.name,
                "synopsis": data.synopsis,
                "description": data.description,
                "quantity": data.quantity,
                "price": data.price,
                "category_id": data.category_id,
                "available": data.available,
                "html_body": data.html_body,
                "parameters": data.parameters,
                "thread_id": data.thread_id,
                "views": 0,
                "created_at": arrow.utcnow().datetime,
                "updated_at": None,
            },
            session=session,
        )

    async def update_by_id(
        self,
        id_: ObjectId,
        data: Any,
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> None:
        """Updates a product in repository.

        Args:
            id_ (ObjectId): The unique identifier of the product.
            data (Any): Data to update product.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def increment_views(
        self, id_: ObjectId, *, session: AsyncIOMotorClientSession | None = None
    ) -> None:
        """Increments a views field for product by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the product.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        """

        await self._mongo_service.update_one(
            collection=self._collection_name,
            filter_={"_id": id_},
            update={"$inc": {"views": 1}},
            session=session,
        )
