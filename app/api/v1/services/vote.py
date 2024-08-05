"""Module that contains vote service class."""

from typing import Any

from bson import ObjectId
from fastapi import BackgroundTasks, Depends, HTTPException, status

from app.api.v1.models import Pagination, Search, Sorting
from app.api.v1.models.vote import Vote, VoteCreateData, VoteData
from app.api.v1.repositories.comment import CommentRepository
from app.api.v1.repositories.vote import VoteRepository
from app.api.v1.services import BaseService
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
        comment_repository: CommentRepository = Depends(),
    ) -> None:
        """Initializes the vote service.

        Args:
            background_tasks (BackgroundTasks): Background tasks.
            redis_service (RedisService): Redis service.
            transaction_manager (TransactionManager): Transaction manager.
            repository (VoteRepository):  An instance of the Vote repository.
            comment_repository (CommentRepository):  An instance of the comment
            repository.

        """

        super().__init__(
            background_tasks=background_tasks,
            redis_service=redis_service,
            transaction_manager=transaction_manager,
        )

        self.repository = repository

        self.comment_repository = comment_repository

    async def get(
        self, filter_: Any, search: Search, sorting: Sorting, pagination: Pagination
    ) -> Any:
        """Retrieves a list of votes based on parameters.

        Args:
            filter_ (Any): Parameters for list filtering.
            search (Search): Parameters for list searching.
            sorting (Sorting): Parameters for sorting.
            pagination (Pagination): Parameters for pagination.

        Returns:
            list[Mapping[str, Any]]: The retrieved list of votes.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def count(self, filter_: Any, search: Search) -> int:
        """Counts votes based on parameters.

        Args:
            filter_ (Any): Parameters for list filtering.
            search (Search): Parameters for list searching.

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

        return await self.repository.get_by_id(id_=id_)

    async def create(self, data: VoteCreateData) -> Vote:
        """Creates a new vote.

        Args:
            data (VoteCreateData): The data for the new vote.

        Returns:
            Vote: Created vote.

        """

        try:
            id_ = await self.repository.create(data=data)

        except EntityDuplicateKeyError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=HTTPErrorMessagesEnum.ENTITY_FIELD_UNIQUENESS.format(
                    entity="Vote", field="comment_id"
                ),
            )

        # increments upvote/downvote counter by one
        await self.comment_repository.add_vote(id_=data.comment_id, value=data.value)

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

    async def update_by_id(self, id_: ObjectId, data: VoteData) -> Vote:
        """Updates a vote by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the vote.
            data (VoteData): Data to update vote.

        Returns:
            Vote: The updated vote.

        """

        vote = await self.repository.get_and_update_by_id(
            id_=id_,
            data=data,
        )

        # updates upvote/downvote counters depends on value
        await self.comment_repository.update_vote(
            id_=vote.comment_id, new_value=data.value
        )

        return vote

    async def delete_by_id(self, id_: ObjectId) -> None:
        """Deletes a vote by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the vote.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def delete(self, item: Vote) -> None:
        """Deletes a vote.

        Args:
            item (Vote): Vote object.

        """

        await self.repository.delete_by_id(id_=item.id)

        # decrements upvote/downvote counter depends on value
        await self.comment_repository.delete_vote(id_=item.comment_id, value=item.value)
