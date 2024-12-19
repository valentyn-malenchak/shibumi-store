"""Module that contains comment service class."""

from typing import Any

from bson import ObjectId
from fastapi import BackgroundTasks, Depends

from app.api.v1.models.comment import Comment, CommentCreateData, CommentUpdateData
from app.api.v1.repositories.comment import CommentRepository
from app.api.v1.services import BaseService
from app.services.mongo.transaction_manager import TransactionManager
from app.services.redis.service import RedisService


class CommentService(BaseService):
    """Comment service for encapsulating business logic."""

    def __init__(
        self,
        background_tasks: BackgroundTasks,
        redis_service: RedisService = Depends(),
        transaction_manager: TransactionManager = Depends(),
        repository: CommentRepository = Depends(),
    ) -> None:
        """Initializes the comment service.

        Args:
            background_tasks (BackgroundTasks): Background tasks.
            redis_service (RedisService): Redis service.
            transaction_manager (TransactionManager): Transaction manager.
            repository (CommentRepository):  An instance of the Comment repository.

        """

        super().__init__(
            background_tasks=background_tasks,
            redis_service=redis_service,
            transaction_manager=transaction_manager,
        )

        self.repository = repository

    async def get(self, **kwargs: Any) -> Any:
        """Retrieves a list of comments based on parameters.

        Args:
            kwargs (Any): Keyword parameters.

        Returns:
            list[Mapping[str, Any]]: The retrieved list of comments.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def count(self, **kwargs: Any) -> int:
        """Counts comments based on parameters.

        Args:
            kwargs (Any): Keyword parameters.

        Returns:
            int: Count of comments.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def get_by_id(self, id_: ObjectId) -> Comment:
        """Retrieves a comment by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the comment.

        Returns:
            Comment: The retrieved comment.

        """
        return await self.repository.get_by_id(id_=id_)

    async def create(self, data: CommentCreateData) -> Comment:
        """Creates a new comment.

        Args:
            data (CommentCreateData): The data for the new comment.

        Returns:
            Comment: Created comment.

        """

        id_ = await self.repository.create(data=data)

        return await self.get_by_id(id_=id_)

    async def update(self, item: Any, data: Any) -> Any:
        """Updates a comment object.

        Args:
            item (Any): Comment object.
            data (Any): Data to update comment.

        Returns:
            Any: The updated comment.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def update_by_id(self, id_: ObjectId, data: CommentUpdateData) -> Comment:
        """Updates a comment by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the comment.
            data (CommentUpdateData): Data to update comment.

        Returns:
            Comment: The updated comment.

        """
        return await self.repository.get_and_update_by_id(
            id_=id_,
            data=data,
        )

    async def delete_by_id(self, id_: ObjectId) -> None:
        """Softly deletes a comment by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the comment.

        """
        await self.repository.delete_by_id(id_=id_)

    async def delete(self, item: Any) -> None:
        """Deletes a comment.

        Args:
            item (Any): Comment object.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError
