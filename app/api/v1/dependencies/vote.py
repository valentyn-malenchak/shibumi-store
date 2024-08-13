"""Contains vote domain dependencies."""

from typing import Annotated

from bson import ObjectId
from fastapi import Depends, Request

from app.api.v1.models.vote import (
    BaseVoteCreateData,
    Vote,
    VoteCreateData,
    VoteData,
)
from app.api.v1.validators.comment import CommentByIdValidator
from app.api.v1.validators.vote import (
    VoteAccessValidator,
    VoteByIdValidator,
    VoteValueUpdateValidator,
)
from app.utils.metas import SingletonMeta
from app.utils.pydantic import ObjectIdAnnotation


class VoteByIdGetDependency(metaclass=SingletonMeta):
    """Vote by identifier get dependency."""

    async def __call__(
        self,
        vote_id: Annotated[ObjectId, ObjectIdAnnotation],
        vote_by_id_validator: VoteByIdValidator = Depends(),
    ) -> Vote:
        """Validates vote by its unique identifier.

        Args:
            vote_id (Annotated[ObjectId, ObjectIdAnnotation]): BSON object
            identifier of requested vote.
            vote_by_id_validator (VoteByIdValidator): Vote by identifier validator.

        Returns:
            Vote: Vote object.

        """
        return await vote_by_id_validator.validate(vote_id=vote_id)


class VoteByIdGetAccessDependency(metaclass=SingletonMeta):
    """Vote by identifier get access dependency."""

    async def __call__(
        self,
        vote: Vote = Depends(VoteByIdGetDependency()),
        vote_access_validator: VoteAccessValidator = Depends(),
    ) -> Vote:
        """Validates access to a specific vote.

        Args:
            vote (Vote): Vote object.
            vote_access_validator (VoteAccessValidator): Vote access validator.

        Returns:
            Vote: Vote object.

        """
        return await vote_access_validator.validate(vote=vote)


class VoteDataCreateDependency(metaclass=SingletonMeta):
    """Vote data create dependency."""

    async def __call__(
        self,
        request: Request,
        vote_data: BaseVoteCreateData,
        comment_by_id_validator: CommentByIdValidator = Depends(),
    ) -> VoteCreateData:
        """Validates data on vote create operation.

        Args:
            request (Request): Current request object.
            vote_data (BaseVoteCreateData): Base vote create data.
            comment_by_id_validator (CommentByIdValidator): Comment by identifier
            validator.

        Returns:
            VoteCreateData: Vote create data.

        """

        await comment_by_id_validator.validate(comment_id=vote_data.comment_id)

        return VoteCreateData(
            value=vote_data.value,
            user_id=request.state.current_user.object.id,
            comment_id=vote_data.comment_id,
        )


class VoteDataUpdateDependency(metaclass=SingletonMeta):
    """Vote data update dependency."""

    async def __call__(
        self,
        vote_data: VoteData,
        vote: Vote = Depends(VoteByIdGetAccessDependency()),
        vote_value_update_validator: VoteValueUpdateValidator = Depends(),
    ) -> VoteData:
        """Validates data on vote update operation.

        Args:
            vote_data (VoteData): Vote data.
            vote (Vote): Vote object.
            vote_value_update_validator (VoteValueUpdateValidator): Vote value update
            validator.

        Returns:
            VoteData: Vote data.

        """

        await vote_value_update_validator.validate(vote=vote, value=vote_data.value)

        return vote_data
