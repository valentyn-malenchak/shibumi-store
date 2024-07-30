"""Module that contains comment repository class."""

from collections.abc import Mapping
from typing import Any

import arrow
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClientSession

from app.api.v1.repositories import BaseRepository
from app.services.mongo.constants import MongoCollectionsEnum


class CommentRepository(BaseRepository):
    """Comment repository for handling data access operations."""

    _collection_name: str = MongoCollectionsEnum.COMMENTS

    @staticmethod
    async def _get_list_query_filter(*_: Any, **__: Any) -> Mapping[str, Any]:
        """Returns a query filter for list of comments.

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
        """Returns a query projection for list of comments.

        Returns:
            Mapping[str, Any] | None: List query projection or None.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    @staticmethod
    def _get_list_default_sorting() -> list[tuple[str, int | Mapping[str, Any]]] | None:
        """Returns default sorting for list of comments.

        Returns:
            list[tuple[str, int | Mapping[str, Any]]] | None: Default sorting.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def get_and_update_by_id(
        self,
        id_: ObjectId,
        *,
        session: AsyncIOMotorClientSession | None = None,
        **fields: Any,
    ) -> Mapping[str, Any]:
        """
        Updates and retrieves a single comment from the repository by its
        unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the comment.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.
            fields (Any): Fields to update comment.

        Returns:
            Mapping[str, Any]: The retrieved comment.

        """

        return await self._mongo_service.find_one_and_update(
            collection=self._collection_name,
            filter_={"_id": id_},
            update={"$set": {**fields, "updated_at": arrow.utcnow().datetime}},
            session=session,
        )

    async def create(
        self, *, session: AsyncIOMotorClientSession | None = None, **fields: Any
    ) -> Any:
        """Creates a new comment in repository.

        Args:
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.
            fields (Any): The fields for the new comment.

        Returns:
            Any: The ID of created comment.

        """
        return await self._mongo_service.insert_one(
            collection=self._collection_name,
            document={
                **fields,
                "upvotes": 0,
                "downvotes": 0,
                "created_at": arrow.utcnow().datetime,
                "updated_at": None,
            },
            session=session,
        )

    async def update_by_id(
        self,
        id_: ObjectId,
        *,
        session: AsyncIOMotorClientSession | None = None,
        **fields: Any,
    ) -> None:
        """Updates a comment in repository.

        Args:
            id_ (ObjectId): The unique identifier of the comment.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.
            fields (Any): Fields to update comment.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def add_vote(
        self,
        id_: ObjectId,
        value: bool,
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> None:
        """Increments a vote counter field for comment by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the comment.
            value (bool): Vote value.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        """

        await self._mongo_service.update_one(
            collection=self._collection_name,
            filter_={"_id": id_},
            update={"$inc": {"upvotes" if value is True else "downvotes": 1}},
            session=session,
        )

    async def update_vote(
        self,
        id_: ObjectId,
        new_value: bool,
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> None:
        """Updates vote counter fields for comment by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the comment.
            new_value (bool): Updated vote value.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        """

        await self._mongo_service.update_one(
            collection=self._collection_name,
            filter_={"_id": id_},
            update={
                "$inc": {"upvotes": 1, "downvotes": -1}
                if new_value is True
                else {"upvotes": -1, "downvotes": 1}
            },
            session=session,
        )

    async def delete_vote(
        self,
        id_: ObjectId,
        value: bool,
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> None:
        """Decrements vote counter field for comment by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the comment.
            value (bool): Vote value.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        """

        await self._mongo_service.update_one(
            collection=self._collection_name,
            filter_={"_id": id_},
            update={"$inc": {"upvotes" if value is True else "downvotes": -1}},
            session=session,
        )
