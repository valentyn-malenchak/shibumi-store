"""Contains vote domain dependencies."""

from typing import Annotated

from bson import ObjectId
from fastapi import Depends

from app.api.v1.models.thread import VoteCreateData, VoteData
from app.api.v1.validators.vote import VoteCreateValidator
from app.utils.pydantic import ObjectIdAnnotation


class VoteDataCreateDependency:
    """Vote data create dependency."""

    async def __call__(
        self,
        thread_id: Annotated[ObjectId, ObjectIdAnnotation],
        comment_id: Annotated[ObjectId, ObjectIdAnnotation],
        vote_data: VoteData,
        vote_create_validator: VoteCreateValidator = Depends(),
    ) -> VoteCreateData:
        """Validates data on vote create operation.

        Args:
            thread_id (Annotated[ObjectId, ObjectIdAnnotation]): BSON object
            identifier of requested thread.
            comment_id (Annotated[ObjectId, ObjectIdAnnotation]): BSON object
            identifier of requested comment.
            vote_data (VoteData): Vote data.
            vote_create_validator (VoteCreateValidator): Vote create validator.

        Returns:
            VoteCreateData: Vote create data.

        """

        return await vote_create_validator.validate(
            thread_id=thread_id,
            comment_id=comment_id,
            value=vote_data.value,
        )
