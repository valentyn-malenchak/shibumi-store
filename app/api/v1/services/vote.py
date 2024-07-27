"""Module that contains vote service class."""

from typing import Any

from bson import ObjectId
from fastapi import BackgroundTasks, Depends, HTTPException, status

from app.api.v1.models.thread import Vote, VoteCreateData
from app.api.v1.repositories.vote import VoteRepository
from app.api.v1.services import BaseService
from app.api.v1.services.comment import CommentService
from app.constants import HTTPErrorMessagesEnum
from app.exceptions import EntityDuplicateKeyError
from app.services.mongo.transaction_manager import TransactionManager
from app.services.redis.service import RedisService


class VoteService(BaseService):
    """Vote service for encapsulating business logic."""

    def __init__(
        self,
        background_tasks: BackgroundTasks,
        redis_service: RedisService = Depends(),
        transaction_manager: TransactionManager = Depends(),
        repository: VoteRepository = Depends(),
        comment_service: CommentService = Depends(),
    ) -> None:
        """Initializes the vote service.

        Args:
            background_tasks (BackgroundTasks): Background tasks.
            redis_service (RedisService): Redis service.
            transaction_manager (TransactionManager): Transaction manager.
            repository (VoteRepository):  An instance of the Vote repository.
            comment_service (CommentService): Comment service.

        """

        super().__init__(
            background_tasks=background_tasks,
            redis_service=redis_service,
            transaction_manager=transaction_manager,
        )

        self.repository = repository

        self.comment_service = comment_service

    async def get(self, *_: Any) -> Any:
        """Retrieves a list of votes based on parameters.

        Args:
            _ (Any): Parameters for list filtering, searching, sorting and pagination.

        Returns:
            list[Mapping[str, Any]]: The retrieved list of votes.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def count(self, *_: Any) -> int:
        """Counts votes based on parameters.

        Args:
            _ (Any): Parameters for list filtering and searching.

        Returns:
            int: Count of votes.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def get_by_id(self, id_: ObjectId) -> Vote:
        """Retrieves a vote by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the vote.

        Returns:
            Vote: The retrieved vote.

        """

        vote = await self.repository.get_by_id(id_=id_)

        return Vote(**vote)

    async def create_raw(self, data: VoteCreateData) -> Any:
        """Creates a raw new vote.

        Args:
            data (VoteCreateData): The data for the new vote.

        Returns:
            Any: The ID of created vote.

        Raises:
            HTTPException: if vote with specified comment is already created for user.

        """
        try:
            return await self.repository.create(
                value=data.value,
                comment_id=data.comment_id,
                user_id=data.user_id,
            )

        except EntityDuplicateKeyError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=HTTPErrorMessagesEnum.ENTITY_FIELD_UNIQUENESS.format(
                    entity="Vote", field="comment_id"
                ),
            )

    async def create(self, data: VoteCreateData) -> Vote:
        """Creates a new vote.

        Args:
            data (VoteCreateData): The data for the new vote.

        Returns:
            Vote: Created vote.

        """

        id_ = await self.create_raw(data=data)

        # increments upvote/downvote counter by one
        await self.comment_service.increment_votes(
            id_=data.comment_id, value=data.value
        )

        return await self.get_by_id(id_=id_)

    async def update(self, item: Any, data: Any) -> Any:
        """Updates a vote object.

        Args:
            item (Any): Vote object.
            data (Any): Data to update vote.

        Returns:
            Any: The updated vote.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def update_by_id(self, id_: ObjectId, data: Any) -> Any:
        """Updates a vote by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the vote.
            data (Any): Data to update vote.

        Returns:
            Any: The updated vote.

        Raises:
            NotImplementedError: This method is not implemented.

        """

        raise NotImplementedError

    async def delete_by_id(self, id_: ObjectId) -> None:
        """Deletes a vote by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the vote.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError
