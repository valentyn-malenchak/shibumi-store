"""Module that contains base repository abstract class."""

import abc
from typing import Any, Dict, List, Mapping

from bson import ObjectId
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClientSession

from app.constants import SortingTypesEnum
from app.services.mongo.service import MongoDBService


class BaseRepository(abc.ABC):
    """Base repository for handling data access operations."""

    _collection_name: str | None = None

    def __init__(self, mongo_service: MongoDBService = Depends()) -> None:
        """Initializes the BaseRepository.

        This method sets up the MongoDB service instance for data access.

        Args:
            mongo_service (MongoDBService): An instance of the MongoDB service.

        """
        self._mongo_service = mongo_service

    @abc.abstractmethod
    async def get(  # noqa: PLR0913
        self,
        search: str | None,
        sort_by: str | None,
        sort_order: SortingTypesEnum,
        page: int,
        page_size: int,
        *_: Any,
        session: AsyncIOMotorClientSession | None = None,
    ) -> List[Any]:
        """Retrieves a list of items based on parameters.

        Args:
            search (str | None): Parameters for list searching.
            sort_by (str | None): Specifies a field for sorting.
            sort_order (SortingTypesEnum): Defines sort order - ascending or descending.
            page (int): Page number.
            page_size (int): Number of items on each page.
            _ (Any): Parameters for list filtering.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            List[Any]: The retrieved list of items.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.

        """
        raise NotImplementedError

    @staticmethod
    def _calculate_skip(page: int, page_size: int) -> int:
        """Calculates count of items to skip for reaching page.

        Args:
            page (int): Page number.
            page_size (int): Number of items on each page.

        Returns:
            int: Skip number.

        """
        return (page - 1) * page_size

    @abc.abstractmethod
    async def _get_list_query_filter(
        self, search: str | None, *_: Any
    ) -> Mapping[str, Any]:
        """Returns a query filter for list.

        Args:
            search (str | None): Parameters for list searching.
            _ (Any): Parameters for list filtering.

        Returns:
            (Mapping[str, Any]): List query filter.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.

        """
        raise NotImplementedError

    @staticmethod
    def _get_list_sorting(
        sort_by: str | None, sort_order: SortingTypesEnum
    ) -> List[tuple[str, int]] | None:
        """Returns list sorting depends on parameters.

        Args:
            sort_by (str | None): Specifies a field for sorting.
            sort_order (SortingTypesEnum): Defines sort order - ascending or descending.

        Returns:
            (List[tuple[str, int]] | None): Sorting.

        """
        sort_value = 1 if sort_order == SortingTypesEnum.ASC else -1

        return [(sort_by, sort_value)] if sort_by else None

    @abc.abstractmethod
    async def count(
        self,
        search: str | None,
        *_: Any,
        session: AsyncIOMotorClientSession | None = None,
    ) -> int:
        """Counts documents based on parameters.

        Args:
            search (str | None): Parameters for list searching.
            _ (Any): Parameters for list filtering.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            int: Count of documents.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.

        """
        raise NotImplementedError

    @abc.abstractmethod
    async def get_by_id(
        self, id_: ObjectId, *, session: AsyncIOMotorClientSession | None = None
    ) -> Any:
        """Retrieves an item from the repository by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the item.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            Any: The retrieved item.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.

        """
        raise NotImplementedError

    @abc.abstractmethod
    async def create(
        self, item: Any, *, session: AsyncIOMotorClientSession | None = None
    ) -> Any:
        """Creates a new item in repository.

        Args:
            item (Any): The data for the new item.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            Any: The ID of created item.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.

        """
        raise NotImplementedError

    @abc.abstractmethod
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

        Raises:
            NotImplementedError: This method must be implemented by subclasses.

        """
        raise NotImplementedError

    @abc.abstractmethod
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

        Raises:
            NotImplementedError: This method must be implemented by subclasses.

        """
        raise NotImplementedError

    @abc.abstractmethod
    async def delete_all(
        self, *, session: AsyncIOMotorClientSession | None = None
    ) -> None:
        """Deletes all items from the repository.

        Args:
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.

        """
        raise NotImplementedError
