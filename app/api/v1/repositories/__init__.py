"""Module that contains base repository abstract class."""

import abc
from collections.abc import Mapping
from typing import Any

from bson import ObjectId
from fastapi import Depends
from injector import inject
from motor.motor_asyncio import AsyncIOMotorClientSession

from app.api.v1.models import Pagination, Search, Sorting
from app.exceptions import EntityIsNotFoundError
from app.services.mongo.constants import SortingTypesEnum, SortingValuesEnum
from app.services.mongo.service import MongoDBService


@inject
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

    async def _get(
        self,
        filter_: Mapping[str, Any] | None = None,
        search: Search | None = None,
        sorting: Sorting | None = None,
        pagination: Pagination | None = None,
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> list[Mapping[str, Any]]:
        """Retrieves a list of documents based on parameters.

        Args:
            filter_ (Mapping[str, Any] | None): Parameters for list filtering.
            Defaults to None.
            search (Search | None): Parameters for list searching. Defaults to None.
            sorting (Sorting | None): Parameters for sorting. Defaults to None.
            pagination (Pagination | None): Parameters for pagination. Defaults to None.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            list[Mapping[str, Any]]: The retrieved list of documents.

        """
        return await self._mongo_service.find(
            collection=self._collection_name,
            filter_=filter_,
            projection=self._get_list_query_projection(),
            sort=self._get_list_sorting(sorting=sorting, search=search),
            skip=self._calculate_skip(pagination),
            limit=pagination.page_size if pagination is not None else None,
            session=session,
        )

    async def get(
        self,
        filter_: Any,
        search: Search | None = None,
        sorting: Sorting | None = None,
        pagination: Pagination | None = None,
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> list[Mapping[str, Any]]:
        """Retrieves a list of documents based on parameters.

        Args:
            filter_ (Any): Parameters for list filtering.
            search (Search | None): Parameters for list searching. Defaults to None.
            sorting (Sorting | None): Parameters for sorting. Defaults to None.
            pagination (Pagination | None): Parameters for pagination. Defaults to None.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            list[Mapping[str, Any]]: The retrieved list of documents.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.

        """
        raise NotImplementedError

    @staticmethod
    def _calculate_skip(pagination: Pagination | None) -> int | None:
        """Calculates count of documents to skip for reaching page.

        Args:
            pagination (Pagination | None): Parameters for pagination.

        Returns:
            int | None: Skip number or None.

        """
        return (
            (pagination.page - 1) * pagination.page_size
            if pagination is not None
            and pagination.page is not None
            and pagination.page_size is not None
            else None
        )

    @abc.abstractmethod
    async def _get_list_query_filter(
        self, filter_: Any, search: Search | None
    ) -> Mapping[str, Any] | None:
        """Returns a query filter for list.

        Args:
            filter_ (Any): Parameters for list filtering.
            search (Search | None): Parameters for list searching.

        Returns:
            Mapping[str, Any] | None: List query filter or None.

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
        sorting: Sorting | None,
        search: Search | None,
    ) -> list[tuple[str, int | Mapping[str, Any]]] | None:
        """Returns list sorting depends on parameters.

        Args:
            sorting (Sorting | None): Parameters for sorting.
            search (Search | None): Parameters for list searching.

        Returns:
            list[tuple[str, int | Mapping[str, Any]]] | None: Sorting.

        """

        if sorting is not None and sorting.sort_by is not None:
            sort_value = (
                SortingValuesEnum.DESC
                if sorting.sort_order == SortingTypesEnum.DESC
                else SortingValuesEnum.ASC
            )

            return [(sorting.sort_by, sort_value)]

        # If search is included to query, return documents sorted by search scores
        return (
            self._get_list_default_sorting()
            if search is None or search.search is None
            else [("score", {"$meta": "textScore"})]
        )

    @staticmethod
    def _apply_list_search(
        query_filter: dict[str, Any], search: Search | None
    ) -> dict[str, Any]:
        """Applies list search to query filter depends on parameters.

        Args:
            search (Search | None): Parameters for list searching.

        Returns:
            dict[str, Any]: Updated query filter.

        """

        if search is not None and search.search is not None:
            query_filter["$text"] = {"$search": search.search}

        return query_filter

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

    async def _count(
        self,
        filter_: Mapping[str, Any] | None = None,
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> int:
        """Counts documents based on parameters.

        Args:
            filter_ (Mapping[str, Any] | None): Parameters for list filtering.
            Defaults to None.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            int: Count of documents.

        """
        return await self._mongo_service.count_documents(
            collection=self._collection_name,
            filter_=filter_,
            session=session,
        )

    async def count(
        self,
        filter_: Any,
        search: Search | None = None,
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> int:
        """Counts documents based on parameters.

        Args:
            filter_ (Any): Parameters for list filtering.
            search (Search | None): Parameters for list searching. Defaults to None.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            int: Count of documents.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.

        """
        raise NotImplementedError

    async def _get_one(
        self,
        *,
        session: AsyncIOMotorClientSession | None = None,
        **filters: Any,
    ) -> Mapping[str, Any]:
        """Retrieves a single document from the repository by filters.

        Args:
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.
            filters (Any): Parameters for document filtering.

        Returns:
            Mapping[str, Any]: The retrieved document.

        Raises:
            EntityIsNotFoundError: In case document is not found.

        """

        document = await self._mongo_service.find_one(
            collection=self._collection_name, filter_=filters, session=session
        )

        if document is None:
            raise EntityIsNotFoundError

        return document

    @abc.abstractmethod
    async def get_by_id(
        self, id_: ObjectId, *, session: AsyncIOMotorClientSession | None = None
    ) -> Any:
        """Retrieves a document from the repository by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the document.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            Any: The retrieved document object.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.

        """
        raise NotImplementedError

    @abc.abstractmethod
    async def get_and_update_by_id(
        self,
        id_: ObjectId,
        data: Any,
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> Any:
        """
        Updates and retrieves a single document from the repository by its
        unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the document.
            data (Any): Data to update document.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            Any: The retrieved document object.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.

        """
        raise NotImplementedError

    @abc.abstractmethod
    async def create(
        self,
        data: Any,
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> Any:
        """Creates a new document in repository.

        Args:
            data (Any): The data for the new document.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

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
        data: Any,
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> None:
        """Updates a document in repository.

        Args:
            id_ (ObjectId): The unique identifier of the document.
            data (Any): Data to update document.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.

        """
        raise NotImplementedError

    async def delete_by_id(
        self,
        id_: ObjectId,
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> None:
        """Deletes a document in repository.

        Args:
            id_ (ObjectId): The unique identifier of the document.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        """

        await self._mongo_service.delete_one(
            collection=self._collection_name, filter_={"_id": id_}, session=session
        )

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
