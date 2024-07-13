"""Contains vote domain validators."""

from typing import Any

from bson import ObjectId
from fastapi import Depends, Request

from app.api.v1.models.thread import VoteCreateData
from app.api.v1.services.vote import VoteService
from app.api.v1.validators import BaseValidator
from app.api.v1.validators.comment import CommentByIdValidator


class BaseVoteValidator(BaseValidator):
    """Base vote validator."""

    def __init__(self, request: Request, vote_service: VoteService = Depends()):
        """Initializes base vote validator.

        Args:
            request (Request): Current request object.
            vote_service (VoteService): Vote service.

        """

        super().__init__(request=request)

        self.vote_service = vote_service

    async def validate(self, *args: Any) -> Any:
        """Validates data.

        Args:
            args (Any): Method arguments.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.

        """
        raise NotImplementedError


class VoteCreateValidator(BaseVoteValidator):
    """Vote create validator."""

    def __init__(
        self,
        request: Request,
        vote_service: VoteService = Depends(),
        comment_by_id_validator: CommentByIdValidator = Depends(),
    ) -> None:
        """Initializes vote create validator.

        Args:
            request (Request): Current request object.
            vote_service (VoteService): Vote service.
            comment_by_id_validator (CommentByIdValidator): Comment by id validator.

        """

        super().__init__(request=request, vote_service=vote_service)

        self.comment_by_id_validator = comment_by_id_validator

    async def validate(
        self, thread_id: ObjectId, comment_id: ObjectId, value: bool
    ) -> VoteCreateData:
        """Checks if thread comment vote can be created.

        Args:
            thread_id (ObjectId): BSON object identifier of requested thread.
            comment_id (ObjectId): BSON object identifier of requested comment.
            value (bool): Vote value.

        Returns:
            VoteCreateData: Vote create data.

        """

        await self.comment_by_id_validator.validate(
            thread_id=thread_id, comment_id=comment_id
        )

        return VoteCreateData(
            value=value,
            user_id=self.request.state.current_user.object.id,
            comment_id=comment_id,
        )
