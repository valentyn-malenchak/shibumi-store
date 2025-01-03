"""Module that contains comment repository class."""

from collections.abc import Mapping
from typing import Any

import arrow
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClientSession

from app.api.v1.models import Search
from app.api.v1.models.comment import Comment, CommentCreateData, CommentUpdateData
from app.api.v1.repositories import BaseRepository
from app.services.mongo.constants import MongoCollectionsEnum


class CommentRepository(BaseRepository):
    """Comment repository for handling data access operations."""

    _collection_name: str = MongoCollectionsEnum.COMMENTS

    async def get(
        self,
        *,
        session: AsyncIOMotorClientSession | None = None,
        **kwargs: Any,
    ) -> list[Mapping[str, Any]]:
        """Retrieves a list of comments based on parameters.

        Args:
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.
            kwargs (Any): Keyword parameters.

        Returns:
            list[Mapping[str, Any]]: The retrieved list of comments.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def _get_list_query_filter(
        self, filter_: Any, search: Search | None
    ) -> Mapping[str, Any] | None:
        """Returns a query filter for list of comments.

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

    async def count(
        self,
        *,
        session: AsyncIOMotorClientSession | None = None,
        **kwargs: Any,
    ) -> int:
        """Counts comments based on parameters.

        Args:
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.
            kwargs (Any): Keyword parameters.

        Returns:
            int: Count of comments.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def get_by_id(
        self, id_: ObjectId, *, session: AsyncIOMotorClientSession | None = None
    ) -> Comment:
        """Retrieves a comment from the repository by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the comment.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            Comment: The retrieved comment object.

        """

        comment = await self._get_one(_id=id_, session=session)

        return Comment(**comment)

    async def get_and_update_by_id(
        self,
        id_: ObjectId,
        data: CommentUpdateData,
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> Comment:
        """
        Updates and retrieves a single comment from the repository by its
        unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the comment.
            data (CommentUpdateData): Data to update comment.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            Comment: The retrieved comment object.

        """

        comment = await self._mongo_service.find_one_and_update(
            collection=self._collection_name,
            filter_={"_id": id_},
            update={"$set": {"body": data.body, "updated_at": arrow.utcnow().datetime}},
            session=session,
        )

        return Comment(**comment)

    async def create(
        self,
        data: CommentCreateData,
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> Any:
        """Creates a new comment in repository.

        Args:
            data (CommentCreateData): The data for the new comment.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        Returns:
            Any: The ID of created comment.

        """

        comment_id = ObjectId()

        return await self._mongo_service.insert_one(
            collection=self._collection_name,
            document={
                "_id": comment_id,
                "body": data.body,
                "thread_id": data.thread_id,
                "user_id": data.user_id,
                "parent_comment_id": data.parent_comment.id
                if data.parent_comment is not None
                else None,
                "path": f"{data.parent_comment.path}/{comment_id}"
                if data.parent_comment is not None
                else f"/{comment_id}",
                "upvotes": 0,
                "downvotes": 0,
                "deleted": "False",
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
        """Updates a comment in repository.

        Args:
            id_ (ObjectId): The unique identifier of the comment.
            data (Any): Data to update comment.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.
            kwargs (Any): Keyword arguments.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def delete_by_id(
        self,
        id_: ObjectId,
        *,
        session: AsyncIOMotorClientSession | None = None,
    ) -> None:
        """Softly deletes a comment in repository.

        Args:
            id_ (ObjectId): The unique identifier of the comment.
            session (AsyncIOMotorClientSession | None): Defines a client session
            if operation is transactional. Defaults to None.

        """

        await self._mongo_service.update_one(
            collection=self._collection_name,
            filter_={"_id": id_},
            update={
                "$set": {
                    "deleted": "True",
                    "updated_at": arrow.utcnow().datetime,
                }
            },
            session=session,
        )

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
