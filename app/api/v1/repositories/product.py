"""Module that contains product repository class."""

from typing import Any, Dict, List, Mapping

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClientSession

from app.api.v1.repositories import BaseRepository
from app.services.mongo.constants import MongoCollectionsEnum


class ProductRepository(BaseRepository):
    """Product repository for handling data access operations."""

    _collection_name: str = MongoCollectionsEnum.PRODUCTS.value

    async def get(
        self,
        *_: Any,
        session: AsyncIOMotorClientSession | None = None,
    ) -> List[Any]:
        """Retrieves a list of products based on parameters.

        Args:
            _ (Any): Parameters for list filtering, searching, sorting and pagination.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            List[Any]: The retrieved list of products.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    @staticmethod
    async def _get_list_query_filter(*_: Any) -> Mapping[str, Any]:
        """Returns a query filter for list.

        Args:
            _ (Any): Parameters for list filtering and searching.

        Returns:
            (Mapping[str, Any]): List query filter.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def count(
        self, *_: Any, session: AsyncIOMotorClientSession | None = None
    ) -> int:
        """Counts documents based on parameters.

        Args:
            _ (Any): Parameters for list filtering and searching.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            int: Count of documents.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def get_by_id(
        self, id_: ObjectId, *, session: AsyncIOMotorClientSession | None = None
    ) -> Mapping[str, Any] | None:
        """Retrieves a product from the repository by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the product.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            Mapping[str, Any] | None: The retrieved product.

        """

        return await self._mongo_service.find_one(
            collection=self._collection_name, filter_={"_id": id_}, session=session
        )

    async def create(
        self, item: Dict[str, Any], *, session: AsyncIOMotorClientSession | None = None
    ) -> Any:
        """Creates a new product in repository.

        Args:
            item (Dict[str, Any]): The data for the new product.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            Any: The ID of created product.

        """
        return await self._mongo_service.insert_one(
            collection=self._collection_name, document=item, session=session
        )

    async def create_many(
        self,
        items: List[Dict[str, Any]],
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> List[Any]:
        """Creates bulk products in the repository.

        Args:
            items (List[Dict[str, Any]]): Products to be created.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            List[Any]: The IDs of created products.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def delete_all(
        self, *, session: AsyncIOMotorClientSession | None = None
    ) -> None:
        """Deletes all products from the repository.

        Args:
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def update_by_id(
        self,
        id_: ObjectId,
        item: Dict[str, Any],
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> None:
        """Updates a product in repository.

        Args:
            id_ (ObjectId): The unique identifier of the product.
            item (Dict[str, Any]): Data to update product.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError
