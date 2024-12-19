"""Module that contains thread repository class."""

from collections.abc import Mapping
from typing import Any

import arrow
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClientSession

from app.api.v1.models import Search
from app.api.v1.models.thread import Thread, ThreadData
from app.api.v1.repositories import BaseRepository
from app.services.mongo.constants import MongoCollectionsEnum


class ThreadRepository(BaseRepository):
    """Thread repository for handling data access operations."""

    _collection_name: str = MongoCollectionsEnum.THREADS

    async def get(
        self,
        *,
        session: AsyncIOMotorClientSession | None = None,
        **kwargs: Any,
    ) -> list[Mapping[str, Any]]:
        """Retrieves a list of threads based on parameters.

        Args:
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.
            kwargs (Any): Keyword parameters.

        Returns:
            list[Mapping[str, Any]]: The retrieved list of threads.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def _get_list_query_filter(
        self, filter_: Any, search: Search | None
    ) -> Mapping[str, Any] | None:
        """Returns a query filter for list of threads.

        Args:
            filter_ (Any): Parameters for list filtering.
            search (Search | None): Parameters for list searching.

        Returns:
            Mapping[str, Any] | None: List query filter or None.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    @staticmethod
    def _get_list_query_projection() -> Mapping[str, Any] | None:
        """Returns a query projection for list of threads.

        Returns:
            Mapping[str, Any] | None: List query projection or None.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    @staticmethod
    def _get_list_default_sorting() -> list[tuple[str, int | Mapping[str, Any]]] | None:
        """Returns default sorting for list of threads.

        Returns:
            list[tuple[str, int | Mapping[str, Any]]] | None: Default sorting.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def count(
        self,
        *,
        session: AsyncIOMotorClientSession | None = None,
        **kwargs: Any,
    ) -> int:
        """Counts threads based on parameters.

        Args:
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.
            kwargs (Any): Keyword parameters.

        Returns:
            int: Count of threads.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def get_by_id(
        self, id_: ObjectId, *, session: AsyncIOMotorClientSession | None = None
    ) -> Thread:
        """Retrieves a thread from the repository by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the thread.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            Thread: The retrieved thread object.

        """

        thread = await self._get_one(_id=id_, session=session)

        return Thread(**thread)

    async def get_and_update_by_id(
        self,
        id_: ObjectId,
        data: ThreadData,
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> Thread:
        """
        Updates and retrieves a single thread from the repository by its
        unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the thread.
            data (ThreadData): Data to update thread.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            Thread: The retrieved thread object.

        """

        thread = await self._mongo_service.find_one_and_update(
            collection=self._collection_name,
            filter_={"_id": id_},
            update={
                "$set": {
                    "name": data.name,
                    "body": data.body,
                    "updated_at": arrow.utcnow().datetime,
                }
            },
            session=session,
        )

        return Thread(**thread)

    async def create(
        self,
        data: ThreadData,
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> Any:
        """Creates a new thread in repository.

        Args:
            data (ThreadData): The data for the new thread.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            Any: The ID of created thread.

        """
        return await self._mongo_service.insert_one(
            collection=self._collection_name,
            document={
                "name": data.name,
                "body": data.body,
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
        **kwargs: Any,
    ) -> None:
        """Updates a thread in repository.

        Args:
            id_ (ObjectId): The unique identifier of the thread.
            data (Any): Data to update thread.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.
            kwargs (Any): Keyword arguments.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError
