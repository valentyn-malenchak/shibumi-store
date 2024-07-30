"""Contains vote domain validators."""

from typing import Any

from bson import ObjectId
from fastapi import Depends, HTTPException, Request, status

from app.api.v1.models.thread import Vote, VoteCreateData, VoteUpdateData
from app.api.v1.services.vote import VoteService
from app.api.v1.validators import BaseValidator
from app.api.v1.validators.comment import CommentByIdValidator
from app.constants import HTTPErrorMessagesEnum
from app.exceptions import EntityIsNotFoundError


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


class VoteByIdValidator(BaseVoteValidator):
    """Vote by identifier validator."""

    def __init__(
        self,
        request: Request,
        vote_service: VoteService = Depends(),
        comment_by_id_validator: CommentByIdValidator = Depends(),
    ) -> None:
        """Initializes comment by identifier validator.

        Args:
            request (Request): Current request object.
            vote_service (VoteService): Vote service.
            comment_by_id_validator (CommentByIdValidator): Comment by id validator.

        """

        super().__init__(request=request, vote_service=vote_service)

        self.comment_by_id_validator = comment_by_id_validator

    async def validate(
        self, thread_id: ObjectId, comment_id: ObjectId, vote_id: ObjectId
    ) -> Vote:
        """Validates requested vote by id.

        Args:
            thread_id (ObjectId): BSON object identifier of requested thread.
            comment_id (ObjectId): BSON object identifier of requested comment.
            vote_id (ObjectId): BSON object identifier of requested vote.

        Returns:
            Vote: Vote object.

        Raises:
            HTTPException: If requested vote is not found or vote does not
            belong to comment.

        """

        comment = await self.comment_by_id_validator.validate(
            thread_id=thread_id, comment_id=comment_id
        )

        try:
            vote = await self.vote_service.get_by_id(id_=vote_id)

        except EntityIsNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=HTTPErrorMessagesEnum.ENTITY_IS_NOT_FOUND.format(entity="Vote"),
            )

        # Check if vote belongs to comment
        if vote.comment_id != comment.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=HTTPErrorMessagesEnum.ENTITIES_ARE_NOT_RELATED.format(
                    child_entity="Vote", parent_entity="comment"
                ),
            )

        return vote


class VoteUserValidator(BaseVoteValidator):
    """Vote user validator."""

    def __init__(
        self,
        request: Request,
        vote_service: VoteService = Depends(),
        vote_by_id_validator: VoteByIdValidator = Depends(),
    ) -> None:
        """Initializes vote user validator.

        Args:
            request (Request): Current request object.
            vote_service (VoteService): Vote service.
            vote_by_id_validator (VoteByIdValidator): Vote by id validator.

        """

        super().__init__(request=request, vote_service=vote_service)

        self.vote_by_id_validator = vote_by_id_validator

    async def validate(
        self, thread_id: ObjectId, comment_id: ObjectId, vote_id: ObjectId
    ) -> Vote:
        """Validates requested vote user.

        Args:
            thread_id (ObjectId): BSON object identifier of requested thread.
            comment_id (ObjectId): BSON object identifier of requested comment.
            vote_id (ObjectId): BSON object identifier of requested vote.

        Returns:
            Vote: Vote object.

        Raises:
            HTTPException: If current user is not related to vote.

        """

        vote = await self.vote_by_id_validator.validate(
            thread_id=thread_id, comment_id=comment_id, vote_id=vote_id
        )

        current_user = self.request.state.current_user

        if vote.user_id != current_user.object.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=HTTPErrorMessagesEnum.VOTE_ACCESS_DENIED,
            )

        return vote


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


class VoteUpdateValidator(BaseVoteValidator):
    """Vote update validator."""

    def __init__(
        self,
        request: Request,
        vote_service: VoteService = Depends(),
        vote_author_validator: VoteUserValidator = Depends(),
    ) -> None:
        """Initializes vote update validator.

        Args:
            request (Request): Current request object.
            vote_service (VoteService): Vote service.
            vote_author_validator (VoteUserValidator): Vote user validator.

        """

        super().__init__(request=request, vote_service=vote_service)

        self.vote_author_validator = vote_author_validator

    async def validate(
        self, thread_id: ObjectId, comment_id: ObjectId, vote_id: ObjectId, value: bool
    ) -> VoteUpdateData:
        """Checks if thread comment vote can be updated.

        Args:
            thread_id (ObjectId): BSON object identifier of requested thread.
            comment_id (ObjectId): BSON object identifier of requested comment.
            vote_id (ObjectId): BSON object identifier of requested vote.
            value (bool): Vote value.

        Returns:
            VoteUpdateData: Vote update data.

        """

        vote = await self.vote_author_validator.validate(
            thread_id=thread_id, comment_id=comment_id, vote_id=vote_id
        )

        if vote.value == value:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=HTTPErrorMessagesEnum.INVALID_VOTE_VALUE,
            )

        return VoteUpdateData(value=value, vote_id=vote.id, comment_id=vote.comment_id)
