"""Contains vote domain dependencies."""

from typing import Annotated

from bson import ObjectId
from fastapi import Depends

from app.api.v1.models.thread import (
    BaseVoteData,
    Vote,
    VoteCreateData,
    VoteUpdateData,
)
from app.api.v1.validators.vote import (
    VoteByIdValidator,
    VoteCreateValidator,
    VoteUpdateValidator,
    VoteUserValidator,
)
from app.utils.pydantic import ObjectIdAnnotation


class VoteByIdDependency:
    """Vote by identifier dependency."""

    async def __call__(
        self,
        thread_id: Annotated[ObjectId, ObjectIdAnnotation],
        comment_id: Annotated[ObjectId, ObjectIdAnnotation],
        vote_id: Annotated[ObjectId, ObjectIdAnnotation],
        vote_by_id_validator: VoteByIdValidator = Depends(),
    ) -> Vote:
        """Checks vote from request by identifier.

        Args:
            thread_id (Annotated[ObjectId, ObjectIdAnnotation]): BSON object
            identifier of requested thread.
            comment_id (Annotated[ObjectId, ObjectIdAnnotation]): BSON object
            identifier of requested comment.
            vote_id (Annotated[ObjectId, ObjectIdAnnotation]): BSON object
            identifier of requested vote.
            vote_by_id_validator (VoteByIdValidator): Vote by identifier
            validator.

        Returns:
            Vote: Vote object.

        """

        return await vote_by_id_validator.validate(
            thread_id=thread_id, comment_id=comment_id, vote_id=vote_id
        )


class VoteUserDependency:
    """Vote user dependency."""

    async def __call__(
        self,
        thread_id: Annotated[ObjectId, ObjectIdAnnotation],
        comment_id: Annotated[ObjectId, ObjectIdAnnotation],
        vote_id: Annotated[ObjectId, ObjectIdAnnotation],
        vote_user_validator: VoteUserValidator = Depends(),
    ) -> Vote:
        """Validates vote user.

        Args:
            thread_id (Annotated[ObjectId, ObjectIdAnnotation]): BSON object
            identifier of requested thread.
            comment_id (Annotated[ObjectId, ObjectIdAnnotation]): BSON object
            identifier of requested comment.
            vote_id (Annotated[ObjectId, ObjectIdAnnotation]): BSON object
            identifier of requested vote.
            vote_user_validator (VoteUserValidator): Vote user validator.

        Returns:
            Vote: Vote object.

        """

        return await vote_user_validator.validate(
            thread_id=thread_id, comment_id=comment_id, vote_id=vote_id
        )


class VoteDataCreateDependency:
    """Vote data create dependency."""

    async def __call__(
        self,
        thread_id: Annotated[ObjectId, ObjectIdAnnotation],
        comment_id: Annotated[ObjectId, ObjectIdAnnotation],
        vote_data: BaseVoteData,
        vote_create_validator: VoteCreateValidator = Depends(),
    ) -> VoteCreateData:
        """Validates data on vote create operation.

        Args:
            thread_id (Annotated[ObjectId, ObjectIdAnnotation]): BSON object
            identifier of requested thread.
            comment_id (Annotated[ObjectId, ObjectIdAnnotation]): BSON object
            identifier of requested comment.
            vote_data (BaseVoteData): Base vote data.
            vote_create_validator (VoteCreateValidator): Vote create validator.

        Returns:
            VoteCreateData: Vote create data.

        """

        return await vote_create_validator.validate(
            thread_id=thread_id,
            comment_id=comment_id,
            value=vote_data.value,
        )


class VoteDataUpdateDependency:
    """Vote data update dependency."""

    async def __call__(
        self,
        thread_id: Annotated[ObjectId, ObjectIdAnnotation],
        comment_id: Annotated[ObjectId, ObjectIdAnnotation],
        vote_id: Annotated[ObjectId, ObjectIdAnnotation],
        vote_data: BaseVoteData,
        vote_update_validator: VoteUpdateValidator = Depends(),
    ) -> VoteUpdateData:
        """Validates data on vote update operation.

        Args:
            thread_id (Annotated[ObjectId, ObjectIdAnnotation]): BSON object
            identifier of requested thread.
            comment_id (Annotated[ObjectId, ObjectIdAnnotation]): BSON object
            identifier of requested comment.
            vote_id (Annotated[ObjectId, ObjectIdAnnotation]): BSON object
            identifier of requested vote.
            vote_data (BaseVoteData): Base vote data.
            vote_update_validator (VoteUpdateValidator): Vote update validator.

        Returns:
            VoteUpdateData: Vote update data.

        """

        return await vote_update_validator.validate(
            thread_id=thread_id,
            comment_id=comment_id,
            vote_id=vote_id,
            value=vote_data.value,
        )
