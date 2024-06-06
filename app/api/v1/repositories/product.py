"""Module that contains product repository class."""

from collections.abc import Mapping
from typing import Any

import arrow
from bson import ObjectId
from injector import inject
from motor.motor_asyncio import AsyncIOMotorClientSession

from app.api.v1.repositories import BaseRepository
from app.constants import ProjectionValuesEnum, SortingValuesEnum
from app.services.mongo.constants import MongoCollectionsEnum


@inject
class ProductRepository(BaseRepository):
    """Product repository for handling data access operations."""

    _collection_name: str = MongoCollectionsEnum.PRODUCTS

    @staticmethod
    async def _get_list_query_filter(
        search: str | None,
        category_id: ObjectId | None = None,
        available: bool | None = None,
        ids: list[ObjectId] | None = None,
        parameters: dict[str, list[Any]] | None = None,
        **_: Any,
    ) -> Mapping[str, Any]:
        """Returns a query filter for list.

        Args:
            search (str | None): Parameters for list searching.
            category_id (ObjectId | None): Category identifier. Defaults to None.
            available (bool | None): Available products filter. Defaults to None.
            ids (list[ObjectId] | None): Filter by list of product identifiers.
            Defaults to None.
            parameters (dict[str, list[Any]] | None): Product parameters filter.
            Defaults to None.
            _ (Any): Parameters for list filtering.

        Returns:
            (Mapping[str, Any]): List query filter.

        """

        query_filter: dict[str, Any] = {}

        if search is not None:
            query_filter["$text"] = {"$search": search}

        if category_id is not None:
            query_filter["category_id"] = category_id

        if available is not None:
            query_filter["available"] = available

        if ids:
            query_filter["_id"] = {"$in": ids}

        if parameters:
            for name, values in parameters.items():
                query_filter[f"parameters.{name}"] = (
                    values[0] if len(values) == 1 else {"$in": values}
                )

        return query_filter

    @staticmethod
    def _get_list_query_projection() -> Mapping[str, Any] | None:
        """Returns a query projection for list.

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
        """Returns list default sorting.

        Returns:
            list[tuple[str, int | Mapping[str, Any]]] | None: Default sorting.

        """
        return [("views", SortingValuesEnum.DESC)]

    async def get_one_and_update_by_id(
        self,
        id_: ObjectId,
        *,
        session: AsyncIOMotorClientSession | None = None,
        **fields: Any,
    ) -> Mapping[str, Any]:
        """
        Updates and retrieves a single product from the repository by its
        unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the product.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.
            fields (Any): Fields to update product.

        Returns:
            Mapping[str, Any]: The retrieved product.

        """

        return await self._mongo_service.find_one_and_update(
            collection=self._collection_name,
            filter_={"_id": id_},
            update={"$set": {**fields, "updated_at": arrow.utcnow().datetime}},
            session=session,
        )

    async def create(
        self, *, session: AsyncIOMotorClientSession | None = None, **fields: Any
    ) -> Any:
        """Creates a new product in repository.

        Args:
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.
            fields (Any): The fields for the new product.

        Returns:
            Any: The ID of created product.

        """

        return await self._mongo_service.insert_one(
            collection=self._collection_name,
            document={
                **fields,
                "views": 0,
                "created_at": arrow.utcnow().datetime,
                "updated_at": None,
            },
            session=session,
        )

    async def update_by_id(
        self,
        id_: ObjectId,
        *,
        session: AsyncIOMotorClientSession | None = None,
        **fields: Any,
    ) -> None:
        """Updates a product in repository.

        Args:
            id_ (ObjectId): The unique identifier of the product.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.
            fields (Any): Fields to update product.

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
