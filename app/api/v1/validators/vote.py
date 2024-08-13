"""Contains vote domain validators."""

from typing import Any

from bson import ObjectId
from fastapi import Depends, HTTPException, Request, status

from app.api.v1.models.vote import Vote
from app.api.v1.services.vote import VoteService
from app.api.v1.validators import BaseValidator
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

    async def validate(self, vote: Vote) -> Vote:
        """Validates if current user has access to requested vote.

        Args:
            vote (Vote): Vote object.

        Returns:
            Vote: Vote object.

        Raises:
            HTTPException: If current user is not related to vote.

        """

        current_user = self.request.state.current_user

        if vote.user_id != current_user.object.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=HTTPErrorMessagesEnum.VOTE_ACCESS_DENIED,
            )

        return vote


class VoteValueUpdateValidator(BaseVoteValidator):
    """Vote value update validator."""

    async def validate(self, vote: Vote, value: bool) -> None:
        """Validates if vote with requested value can be updated.

        Args:
            vote (Vote): Vote object.
            value (bool): Vote value.

        """

        if vote.value == value:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=HTTPErrorMessagesEnum.INVALID_VOTE_VALUE,
            )
