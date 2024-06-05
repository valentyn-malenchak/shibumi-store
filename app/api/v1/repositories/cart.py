"""Module that contains cart repository class."""

from collections.abc import Mapping
from typing import Any

import arrow
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClientSession

from app.api.v1.repositories import BaseRepository
from app.services.mongo.constants import MongoCollectionsEnum
from app.utils.pydantic import PositiveInt


class CartRepository(BaseRepository):
    """Cart repository for handling data access operations."""

    _collection_name: str = MongoCollectionsEnum.CARTS

    @staticmethod
    async def _get_list_query_filter(*_: Any, **__: Any) -> Mapping[str, Any]:
        """Returns a query filter for list.

        Args:
            _ (Any): Parameters for list searching.
            __ (Any): Parameters for list filtering.

        Returns:
            (Mapping[str, Any]): List query filter.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    @staticmethod
    def _get_list_query_projection() -> Mapping[str, Any] | None:
        """Returns a query projection for list.

        Returns:
            Mapping[str, Any] | None: List query projection or None.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    @staticmethod
    def get_list_default_sorting() -> list[tuple[str, int | Mapping[str, Any]]] | None:
        """Returns list default sorting.

        Returns:
            list[tuple[str, int | Mapping[str, Any]]] | None: Default sorting.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def get_by_user_id(
        self, user_id: ObjectId, *, session: AsyncIOMotorClientSession | None = None
    ) -> Mapping[str, Any] | None:
        """Retrieves an item from the repository by user unique identifier.

        Args:
            user_id (ObjectId): BSON object identifier of requested user.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            Mapping[str, Any] | None: The retrieved item.

        """

        return await self._mongo_service.find_one(
            collection=self._collection_name,
            filter_={"user_id": user_id},
            session=session,
        )

    async def add_product(
        self,
        user_id: ObjectId,
        product_id: ObjectId,
        quantity: PositiveInt,
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> Mapping[str, Any]:
        """Adds new product to the cart.

        Args:
            user_id (ObjectId): BSON object identifier of requested user.
            product_id (ObjectId): BSON object identifier of requested product.
            quantity (PositiveInt): Product quantity.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            Mapping[str, Any]: The retrieved item.

        """

        return await self._mongo_service.find_one_and_update(
            collection=self._collection_name,
            filter_={"user_id": user_id},
            update={
                "$push": {"products": {"id": product_id, "quantity": quantity}},
                "$set": {"updated_at": arrow.utcnow().datetime},
            },
            session=session,
        )

    async def update_product(
        self,
        user_id: ObjectId,
        product_id: ObjectId,
        quantity: PositiveInt,
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> Mapping[str, Any]:
        """Updates product in the cart.

        Args:
            user_id (ObjectId): BSON object identifier of requested user.
            product_id (ObjectId): BSON object identifier of requested product.
            quantity (PositiveInt): Product quantity.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            Mapping[str, Any]: The retrieved item.

        """

        return await self._mongo_service.find_one_and_update(
            collection=self._collection_name,
            filter_={"user_id": user_id, "products.id": product_id},
            update={
                "$set": {
                    "products.$.quantity": quantity,
                    "updated_at": arrow.utcnow().datetime,
                }
            },
            session=session,
        )

    async def delete_product(
        self,
        user_id: ObjectId,
        product_id: ObjectId,
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> Mapping[str, Any]:
        """Deletes product from the cart.

        Args:
            user_id (ObjectId): BSON object identifier of requested user.
            product_id (ObjectId): BSON object identifier of requested product.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            Mapping[str, Any]: The retrieved item.

        """

        return await self._mongo_service.find_one_and_update(
            collection=self._collection_name,
            filter_={"user_id": user_id},
            update={
                "$pull": {"products": {"id": product_id}},
                "$set": {"updated_at": arrow.utcnow().datetime},
            },
            session=session,
        )
