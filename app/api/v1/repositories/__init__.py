"""Module that contains base repository abstract class."""

import abc
from collections.abc import Mapping
from typing import Any

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
    ) -> list[Mapping[str, Any]]:
        """Retrieves a list of documents based on parameters.

        Args:
            search (str | None): Parameters for list searching.
            sort_by (str | None): Specifies a field for sorting.
            sort_order (SortingTypesEnum | None): Defines sort order - ascending
            or descending.
            page (int | None): Page number.
            page_size (int | None): Number of documents on each page.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.
            filters (Any): Parameters for list filtering.

        Returns:
            list[Mapping[str, Any]]: The retrieved list of documents.

        """

        return await self._mongo_service.find(
            collection=self._collection_name,
            filter_=await self._get_list_query_filter(search, **filters),
            projection=self._get_list_query_projection(),
            sort=self._get_list_sorting(
                sort_by=sort_by, sort_order=sort_order, search=search is not None
            ),
            skip=self._calculate_skip(page=page, page_size=page_size),
            limit=page_size,
            session=session,
        )

    @staticmethod
    def _calculate_skip(page: int | None, page_size: int | None) -> int | None:
        """Calculates count of documents to skip for reaching page.

        Args:
            page (int | None): Page number.
            page_size (int | None): Number of documents on each page.

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

        Raises:
            NotImplementedError: This method must be implemented by subclasses.

        """
        raise NotImplementedError

    @staticmethod
    @abc.abstractmethod
    def _get_list_query_projection() -> Mapping[str, Any] | None:
        """Returns a query projection for list.

        Returns:
            Mapping[str, Any] | None: List query projection or None.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.

        """
        raise NotImplementedError

    def _get_list_sorting(
        self,
        sort_by: str | None,
        sort_order: SortingTypesEnum | None,
        search: bool = False,
    ) -> list[tuple[str, int | Mapping[str, Any]]] | None:
        """Returns list sorting depends on parameters.

        Args:
            sort_by (str | None): Specifies a field for sorting.
            sort_order (SortingTypesEnum | None): Defines sort order - ascending
            or descending.
            search (bool): Defines if search is included in query. Defaults to False.

        Returns:
            list[tuple[str, int | Mapping[str, Any]]] | None: Sorting.

        """

        if sort_by is not None:
            sort_value = (
                SortingValuesEnum.DESC
                if sort_order == SortingTypesEnum.DESC
                else SortingValuesEnum.ASC
            )

            return [(sort_by, sort_value)]

        # If search is included to query, return documents sorted by search scores
        return (
            self._get_list_default_sorting()
            if search is False
            else [("score", {"$meta": "textScore"})]
        )

    @staticmethod
    @abc.abstractmethod
    def _get_list_default_sorting() -> list[tuple[str, int | Mapping[str, Any]]] | None:
        """Returns list default sorting.

        Returns:
            list[tuple[str, int | Mapping[str, Any]]] | None: Default sorting.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.

        """
        raise NotImplementedError

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
        """Retrieves a document from the repository by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the document.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            Mapping[str, Any] | None: The retrieved document.

        """

        return await self._mongo_service.find_one(
            collection=self._collection_name, filter_={"_id": id_}, session=session
        )

    @abc.abstractmethod
    async def get_one_and_update_by_id(
        self,
        id_: ObjectId,
        *,
        session: AsyncIOMotorClientSession | None = None,
        **fields: Any,
    ) -> Mapping[str, Any]:
        """
        Updates and retrieves a single document from the repository by its
        unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the document.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.
            fields (Any): Fields to update document.

        Returns:
            Mapping[str, Any]: The retrieved document.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.

        """
        raise NotImplementedError

    @abc.abstractmethod
    async def create(
        self, *, session: AsyncIOMotorClientSession | None = None, **fields: Any
    ) -> Any:
        """Creates a new document in repository.

        Args:
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.
            fields (Any): The fields for the new document.

        Returns:
            Any: The ID of created document.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.

        """
        raise NotImplementedError

    async def create_many(
        self,
        documents: list[dict[str, Any]],
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> list[Any]:
        """Creates bulk documents in the repository.

        Args:
            documents (list[dict[str, Any]]): Documents to be created.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            list[Any]: The IDs of created documents.

        """

        return await self._mongo_service.insert_many(
            collection=self._collection_name,
            documents=documents,
            session=session,
        )

    @abc.abstractmethod
    async def update_by_id(
        self,
        id_: ObjectId,
        *,
        session: AsyncIOMotorClientSession | None = None,
        **fields: Any,
    ) -> None:
        """Updates a document in repository.

        Args:
            id_ (ObjectId): The unique identifier of the document.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.
            fields (Any): Fields to update document.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.

        """
        raise NotImplementedError

    async def delete_all(
        self, *, session: AsyncIOMotorClientSession | None = None
    ) -> None:
        """Deletes all documents from the repository.

        Args:
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        """

        await self._mongo_service.delete_many(
            collection=self._collection_name, session=session
        )
