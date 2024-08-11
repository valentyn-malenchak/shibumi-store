"""Contains vote domain dependencies."""

from typing import Annotated

from bson import ObjectId
from fastapi import Depends

from app.api.v1.models.vote import (
    BaseVoteCreateData,
    Vote,
    VoteCreateData,
    VoteData,
)
from app.api.v1.validators.vote import (
    VoteAccessValidator,
    VoteCreateValidator,
    VoteValueUpdateValidator,
)
from app.utils.pydantic import ObjectIdAnnotation


class VoteAccessDependency:
    """Vote access dependency."""

    async def __call__(
        self,
        vote_id: Annotated[ObjectId, ObjectIdAnnotation],
        vote_access_validator: VoteAccessValidator = Depends(),
    ) -> Vote:
        """Validates vote access.

        Args:
            vote_id (Annotated[ObjectId, ObjectIdAnnotation]): BSON object
            identifier of requested vote.
            vote_access_validator (VoteAccessValidator): Vote access validator.

        Returns:
            Vote: Vote object.

        """

        return await vote_access_validator.validate(vote_id=vote_id)


class VoteDataCreateDependency:
    """Vote data create dependency."""

    async def __call__(
        self,
        vote_data: BaseVoteCreateData,
        vote_create_validator: VoteCreateValidator = Depends(),
    ) -> VoteCreateData:
        """Validates data on vote create operation.

        Args:
            vote_data (BaseVoteCreateData): Base vote create data.
            vote_create_validator (VoteCreateValidator): Vote create validator.

        Returns:
            VoteCreateData: Vote create data.

        """

        return await vote_create_validator.validate(
            comment_id=vote_data.comment_id,
            value=vote_data.value,
        )


class VoteDataUpdateDependency:
    """Vote data update dependency."""

    async def __call__(
        self,
        vote_data: VoteData,
        vote_value_update_validator: VoteValueUpdateValidator = Depends(),
    ) -> VoteData:
        """Validates data on vote update operation.

        Args:
            vote_data (VoteData): Vote data.
            vote_value_update_validator (VoteValueUpdateValidator): Vote value update
            validator.

        Returns:
            VoteData: Vote data.

        """

        await vote_value_update_validator.validate(value=vote_data.value)

        return vote_data
