"""Contains vote domain validators."""

from typing import Any

from bson import ObjectId
from fastapi import Depends, HTTPException, Request, status

from app.api.v1.models.vote import Vote, VoteCreateData
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

    async def validate(self, vote_id: ObjectId) -> Vote:
        """Validates requested vote by identifier.

        Args:
            vote_id (ObjectId): BSON object identifier of requested vote.

        Returns:
            Vote: Vote object.

        Raises:
            HTTPException: If requested vote is not found.

        """

        try:
            vote = await self.vote_service.get_by_id(id_=vote_id)

        except EntityIsNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=HTTPErrorMessagesEnum.ENTITY_IS_NOT_FOUND.format(entity="Vote"),
            )

        return vote


class VoteAccessValidator(BaseVoteValidator):
    """Vote access validator."""

    def __init__(
        self,
        request: Request,
        vote_service: VoteService = Depends(),
        vote_by_id_validator: VoteByIdValidator = Depends(),
    ) -> None:
        """Initializes vote access validator.

        Args:
            request (Request): Current request object.
            vote_service (VoteService): Vote service.
            vote_by_id_validator (VoteByIdValidator): Vote by identifier validator.

        """

        super().__init__(request=request, vote_service=vote_service)

        self.vote_by_id_validator = vote_by_id_validator

    async def validate(self, vote_id: ObjectId) -> Vote:
        """Validates if user has access to vote.

        Args:
            vote_id (ObjectId): BSON object identifier of requested vote.

        Returns:
            Vote: Vote object.

        Raises:
            HTTPException: If current user is not related to vote.

        """

        vote = await self.vote_by_id_validator.validate(vote_id=vote_id)

        current_user = self.request.state.current_user

        if vote.user_id != current_user.object.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=HTTPErrorMessagesEnum.VOTE_ACCESS_DENIED,
            )

        # Save vote object in request
        self.request.state.vote = vote

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
            comment_by_id_validator (CommentByIdValidator): Comment by
            identifier validator.

        """

        super().__init__(request=request, vote_service=vote_service)

        self.comment_by_id_validator = comment_by_id_validator

    async def validate(self, comment_id: ObjectId, value: bool) -> VoteCreateData:
        """Validates if vote can be created.

        Args:
            comment_id (ObjectId): BSON object identifier of requested comment.
            value (bool): Vote value.

        Returns:
            VoteCreateData: Vote create data.

        """

        await self.comment_by_id_validator.validate(comment_id=comment_id)

        return VoteCreateData(
            value=value,
            user_id=self.request.state.current_user.object.id,
            comment_id=comment_id,
        )


class VoteValueUpdateValidator(BaseVoteValidator):
    """Vote value update validator."""

    async def validate(self, value: bool) -> None:
        """Validates if vote with requested value can be updated.

        Args:
            value (bool): Vote value.

        """

        vote = self.request.state.vote

        if vote.value == value:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=HTTPErrorMessagesEnum.INVALID_VOTE_VALUE,
            )
