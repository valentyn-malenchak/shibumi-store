"""Module that contains vote repository class."""

from collections.abc import Mapping
from typing import Any

import arrow
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClientSession
from pymongo.errors import DuplicateKeyError

from app.api.v1.models import Search
from app.api.v1.models.vote import Vote, VoteCreateData, VoteData
from app.api.v1.repositories import BaseRepository
from app.exceptions import EntityDuplicateKeyError
from app.services.mongo.constants import MongoCollectionsEnum


class VoteRepository(BaseRepository):
    """Vote repository for handling data access operations."""

    _collection_name: str = MongoCollectionsEnum.VOTES

    async def _get_list_query_filter(
        self, filter_: Any, search: Search | None
    ) -> Mapping[str, Any]:
        """Returns a query filter for list of votes.

        Args:
            filter_ (Any): Parameters for list filtering.
            search (Search | None): Parameters for list searching.

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

    async def get_by_id(
        self, id_: ObjectId, *, session: AsyncIOMotorClientSession | None = None
    ) -> Vote:
        """Retrieves a vote from the repository by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the vote.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            Vote: The retrieved vote object.

        """

        vote = await self._get_one(_id=id_, session=session)

        return Vote(**vote)

    async def get_and_update_by_id(
        self,
        id_: ObjectId,
        data: VoteData,
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> Vote:
        """
        Updates and retrieves a single vote from the repository by its
        unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the vote.
            data (VoteData): Data to update vote.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            Vote: The retrieved vote object.

        """

        vote = await self._mongo_service.find_one_and_update(
            collection=self._collection_name,
            filter_={"_id": id_},
            update={
                "$set": {"value": data.value, "updated_at": arrow.utcnow().datetime}
            },
            session=session,
        )

        return Vote(**vote)

    async def create(
        self,
        data: VoteCreateData,
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> Any:
        """Creates a new vote in repository.

        Args:
            data (VoteCreateData): The data for the new vote.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            Any: The ID of created vote.

        """

        try:
            return await self._mongo_service.insert_one(
                collection=self._collection_name,
                document={
                    "value": data.value,
                    "comment_id": data.comment_id,
                    "user_id": data.user_id,
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
        data: Any,
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> None:
        """Updates a vote in repository.

        Args:
            id_ (ObjectId): The unique identifier of the vote.
            data (Any): Data to update vote.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError
