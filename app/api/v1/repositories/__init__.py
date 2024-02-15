"""Module that contains base repository abstract class."""

import abc
from typing import Any, Dict, List, Mapping

from bson import ObjectId
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClientSession

from app.constants import SortingTypesEnum, SortingValuesEnum
from app.services.mongo.service import MongoDBService


class BaseRepository(abc.ABC):
    """Base repository for handling data access operations."""

    _collection_name: str

    def __init__(self, mongo_service: MongoDBService = Depends()) -> None:
        """Initializes the BaseRepository.

        This method sets up the MongoDB service instance for data access.

        Args:
            mongo_service (MongoDBService): An instance of the MongoDB service.

        """
        self._mongo_service = mongo_service

    async def get(  # noqa: PLR0913
        self,
        search: str | None,
        sort_by: str | None,
        sort_order: SortingTypesEnum | None,
        page: int | None,
        page_size: int | None,
        session: AsyncIOMotorClientSession | None = None,
        **filters: Any,
    ) -> List[Mapping[str, Any]]:
        """Retrieves a list of items based on parameters.

        Args:
            search (str | None): Parameters for list searching.
            sort_by (str | None): Specifies a field for sorting.
            sort_order (SortingTypesEnum | None): Defines sort order - ascending
            or descending.
            page (int | None): Page number.
            page_size (int | None): Number of items on each page.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.
            filters (Any): Parameters for list filtering.

        Returns:
            List[Mapping[str, Any]]: The retrieved list of items.

        """

        return await self._mongo_service.find(
            collection=self._collection_name,
            filter_=await self._get_list_query_filter(search, **filters),
            sort=self._get_list_sorting(sort_by=sort_by, sort_order=sort_order),
            skip=self._calculate_skip(page=page, page_size=page_size),
            limit=page_size,
            session=session,
        )

    @staticmethod
    def _calculate_skip(page: int | None, page_size: int | None) -> int | None:
        """Calculates count of items to skip for reaching page.

        Args:
            page (int | None): Page number.
            page_size (int | None): Number of items on each page.

        Returns:
            int | None: Skip number or None.

        """
        return (
            (page - 1) * page_size
            if page is not None and page_size is not None
            else None
        )

    @abc.abstractmethod
    async def _get_list_query_filter(
        self, search: str | None, **filters: Any
    ) -> Mapping[str, Any]:
        """Returns a query filter for list.

        Args:
            search (str | None): Parameters for list searching.
            filters (Any): Parameters for list filtering.

        Returns:
            Mapping[str, Any]: List query filter.

        """
        raise NotImplementedError

    @staticmethod
    def _get_list_sorting(
        sort_by: str | None, sort_order: SortingTypesEnum | None
    ) -> List[tuple[str, int]] | None:
        """Returns list sorting depends on parameters.

        Args:
            sort_by (str | None): Specifies a field for sorting.
            sort_order (SortingTypesEnum | None): Defines sort order - ascending
            or descending.

        Returns:
            List[tuple[str, int]] | None: Sorting.

        """
        return (
            [
                (
                    sort_by,
                    SortingValuesEnum.DESC.value
                    if sort_order == SortingTypesEnum.DESC
                    else SortingValuesEnum.ASC.value,
                )
            ]
            if sort_by is not None
            else None
        )

    async def count(
        self,
        search: str | None,
        session: AsyncIOMotorClientSession | None = None,
        **filters: Any,
    ) -> int:
        """Counts documents based on parameters.

        Args:
            search (str | None): Parameters for list searching.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.
            filters (Any): Parameters for list filtering.

        Returns:
            int: Count of documents.

        """

        return await self._mongo_service.count_documents(
            collection=self._collection_name,
            filter_=await self._get_list_query_filter(search, **filters),
            session=session,
        )

    async def get_by_id(
        self, id_: ObjectId, *, session: AsyncIOMotorClientSession | None = None
    ) -> Mapping[str, Any] | None:
        """Retrieves an item from the repository by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the item.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            Mapping[str, Any] | None: The retrieved item.

        """

        return await self._mongo_service.find_one(
            collection=self._collection_name, filter_={"_id": id_}, session=session
        )

    async def create(
        self, item: Dict[str, Any], *, session: AsyncIOMotorClientSession | None = None
    ) -> Any:
        """Creates a new item in repository.

        Args:
            item (Dict[str, Any]): The data for the new item.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            Any: The ID of created item.

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
        """Creates bulk items in the repository.

        Args:
            items (List[Dict[str, Any]]): Items to be created.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            List[Any]: The IDs of created items.

        """

        return await self._mongo_service.insert_many(
            collection=self._collection_name,
            documents=items,
            session=session,
        )

    async def update_by_id(
        self,
        id_: ObjectId,
        item: Dict[str, Any],
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> None:
        """Updates an item in repository.

        Args:
            id_ (ObjectId): The unique identifier of the item.
            item (Dict[str, Any]): Data to update item.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        """

        await self._mongo_service.update_one(
            collection=self._collection_name,
            filter_={"_id": id_},
            update={"$set": item},
            session=session,
        )

    async def delete_all(
        self, *, session: AsyncIOMotorClientSession | None = None
    ) -> None:
        """Deletes all items from the repository.

        Args:
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        """

        await self._mongo_service.delete_many(
            collection=self._collection_name, session=session
        )
