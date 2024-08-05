"""Module that contains cart repository class."""

from collections.abc import Mapping
from typing import Any

import arrow
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClientSession

from app.api.v1.models.cart import Cart, CartCreateData
from app.api.v1.repositories import BaseRepository
from app.services.mongo.constants import MongoCollectionsEnum
from app.utils.pydantic import PositiveInt


class CartRepository(BaseRepository):
    """Cart repository for handling data access operations."""

    _collection_name: str = MongoCollectionsEnum.CARTS

    @staticmethod
    async def _get_list_query_filter(*_: Any, **__: Any) -> Mapping[str, Any]:
        """Returns a query filter for list of carts.

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
        """Returns a query projection for list of carts.

        Returns:
            Mapping[str, Any] | None: List query projection or None.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    @staticmethod
    def _get_list_default_sorting() -> list[tuple[str, int | Mapping[str, Any]]] | None:
        """Returns default sorting for list of carts.

        Returns:
            list[tuple[str, int | Mapping[str, Any]]] | None: Default sorting.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def get_by_id(
        self, id_: ObjectId, *, session: AsyncIOMotorClientSession | None = None
    ) -> Cart:
        """Retrieves a cart from the repository by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the cart.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            Cart: The retrieved cart object.

        """

        cart = await self._get_one(_id=id_, session=session)

        return Cart(**cart)

    async def get_and_update_by_id(
        self,
        id_: ObjectId,
        data: Any,
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> Any:
        """
        Updates and retrieves a single cart from the repository by its
        unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the cart.
            data (Any): Data to update cart.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            Any: The retrieved cart object.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def create(
        self,
        data: CartCreateData,
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> Any:
        """Creates a new cart in repository.

        Args:
            data (CartCreateData): The data for the new cart.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            Any: The ID of created cart.

        """

        return await self._mongo_service.insert_one(
            collection=self._collection_name,
            document={
                "user_id": data.user_id,
                "products": [],
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
        """Updates a cart in repository.

        Args:
            id_ (ObjectId): The unique identifier of the cart.
            data (Any): Data to update cart.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def get_by_user_id(
        self,
        user_id: ObjectId,
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> Cart:
        """Retrieves a cart from the repository by user identifier.

        Args:
            user_id (ObjectId): The unique identifier of the user.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            Cart: The retrieved cart object.

        """

        cart = await self._get_one(user_id=user_id, session=session)

        return Cart(**cart)

    async def add_product(
        self,
        id_: ObjectId,
        product_id: ObjectId,
        quantity: PositiveInt,
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> Mapping[str, Any]:
        """Adds new product to the cart.

        Args:
            id_ (ObjectId): BSON object identifier of requested cart.
            product_id (ObjectId): BSON object identifier of requested product.
            quantity (PositiveInt): Product quantity.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            Mapping[str, Any]: The retrieved cart.

        """

        return await self._mongo_service.find_one_and_update(
            collection=self._collection_name,
            filter_={"_id": id_},
            update={
                "$push": {"products": {"id": product_id, "quantity": quantity}},
                "$set": {"updated_at": arrow.utcnow().datetime},
            },
            session=session,
        )

    async def update_product(
        self,
        id_: ObjectId,
        product_id: ObjectId,
        quantity: PositiveInt,
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> Mapping[str, Any]:
        """Updates product in the cart.

        Args:
            id_ (ObjectId): BSON object identifier of requested cart.
            product_id (ObjectId): BSON object identifier of requested product.
            quantity (PositiveInt): Product quantity.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            Mapping[str, Any]: The retrieved cart.

        """

        return await self._mongo_service.find_one_and_update(
            collection=self._collection_name,
            filter_={"_id": id_, "products.id": product_id},
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
        id_: ObjectId,
        product_id: ObjectId,
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> Mapping[str, Any]:
        """Deletes product from the cart.

        Args:
            id_ (ObjectId): BSON object identifier of requested cart.
            product_id (ObjectId): BSON object identifier of requested product.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            Mapping[str, Any]: The retrieved cart.

        """

        return await self._mongo_service.find_one_and_update(
            collection=self._collection_name,
            filter_={"_id": id_},
            update={
                "$pull": {"products": {"id": product_id}},
                "$set": {"updated_at": arrow.utcnow().datetime},
            },
            session=session,
        )
