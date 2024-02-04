"""Module that contains categories repository class."""

from typing import Any, Dict, List, Mapping

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClientSession

from app.api.v1.repositories import BaseRepository
from app.constants import SortingTypesEnum
from app.services.mongo.constants import MongoCollectionsEnum


class CategoryRepository(BaseRepository):
    """Category repository for handling data access operations."""

    _collection_name: str = MongoCollectionsEnum.CATEGORIES.value

    async def get(
        self,
        *_: Any,
        path: str | None = None,
        session: AsyncIOMotorClientSession | None = None,
    ) -> List[Any]:
        """Retrieves a list of categories based on parameters.

        Args:
            _ (Any): Parameters for list searching, sorting and pagination.
            path (str | None): Category tree path filtering. Defaults to None.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            List[Any]: The retrieved list of categories.

        """

        return await self._mongo_service.find(
            collection=self._collection_name,
            filter_=self._get_list_query_filter(path=path),
            sort=self._get_list_sorting(sort_by="_id", sort_order=SortingTypesEnum.ASC),
            session=session,
        )

    @staticmethod
    def _get_list_query_filter(*_: Any, path: str | None = None) -> Mapping[str, Any]:
        """Returns a query filter for list.

        Args:
            _ (Any): Parameters for list searching.
            path (str | None): Category tree path filtering. Defaults to None.

        Returns:
            (Mapping[str, Any]): List query filter.

        """

        query_filter = {}

        if path is not None:
            query_filter["path"] = {"$regex": f"^{path}"}

        return query_filter

    async def count(
        self,
        *_: Any,
        path: str | None = None,
        session: AsyncIOMotorClientSession | None = None,
    ) -> int:
        """Counts documents based on parameters.

        Args:
            _ (Any): Parameters for list filtering.
            path (str | None): Category tree path filtering. Defaults to None.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            int: Count of documents.

        """
        return await self._mongo_service.count_documents(
            collection=self._collection_name,
            filter_=self._get_list_query_filter(path=path),
            session=session,
        )

    async def get_by_id(
        self, id_: ObjectId, *, session: AsyncIOMotorClientSession | None = None
    ) -> Any:
        """Retrieves a category from the repository by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the category.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            Any: The retrieved category.


        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def create(
        self, item: Any, *, session: AsyncIOMotorClientSession | None = None
    ) -> Any:
        """Creates a new category in repository.

        Args:
            item (Any): The data for the new category.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            Any: The ID of created category.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def create_many(
        self,
        items: List[Dict[str, Any]],
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> List[Any]:
        """Creates bulk categories in the repository.

        Args:
            items (List[Dict[str, Any]]): Categories to be created.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            List[Any]: The IDs of created categories.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def delete_all(
        self, *, session: AsyncIOMotorClientSession | None = None
    ) -> None:
        """Deletes all categories from the repository.

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
        """Updates a category in repository.

        Args:
            id_ (ObjectId): The unique identifier of the category.
            item (Any): Data to update category.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError
