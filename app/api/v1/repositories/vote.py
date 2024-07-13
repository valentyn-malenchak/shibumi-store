"""Module that contains vote repository class."""

from collections.abc import Mapping
from typing import Any

import arrow
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClientSession
from pymongo.errors import DuplicateKeyError

from app.api.v1.repositories import BaseRepository
from app.exceptions import EntityDuplicateKeyError
from app.services.mongo.constants import MongoCollectionsEnum


class VoteRepository(BaseRepository):
    """Vote repository for handling data access operations."""

    _collection_name: str = MongoCollectionsEnum.VOTES

    @staticmethod
    async def _get_list_query_filter(*_: Any, **__: Any) -> Mapping[str, Any]:
        """Returns a query filter for list of votes.

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
        """Returns a query projection for list of votes.

        Returns:
            Mapping[str, Any] | None: List query projection or None.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    @staticmethod
    def _get_list_default_sorting() -> list[tuple[str, int | Mapping[str, Any]]] | None:
        """Returns default sorting for list of votes.

        Returns:
            list[tuple[str, int | Mapping[str, Any]]] | None: Default sorting.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def get_one_and_update_by_id(
        self,
        id_: ObjectId,
        *,
        session: AsyncIOMotorClientSession | None = None,
        **fields: Any,
    ) -> Mapping[str, Any]:
        """
        Updates and retrieves a single vote from the repository by its
        unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the vote.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.
            fields (Any): Fields to update vote.

        Returns:
            Mapping[str, Any]: The retrieved vote.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def create(
        self, *, session: AsyncIOMotorClientSession | None = None, **fields: Any
    ) -> Any:
        """Creates a new vote in repository.

        Args:
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.
            fields (Any): The fields for the new vote.

        Returns:
            Any: The ID of created vote.

        """

        try:
            return await self._mongo_service.insert_one(
                collection=self._collection_name,
                document={
                    **fields,
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                session=session,
            )

        except DuplicateKeyError:
            raise EntityDuplicateKeyError

    async def update_by_id(
        self,
        id_: ObjectId,
        *,
        session: AsyncIOMotorClientSession | None = None,
        **fields: Any,
    ) -> None:
        """Updates a vote in repository.

        Args:
            id_ (ObjectId): The unique identifier of the vote.
            id_ (ObjectId): The unique identifier of the vote.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.
            fields (Any): Fields to update vote.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError
