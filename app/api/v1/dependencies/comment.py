"""Contains comment domain dependencies."""

from typing import Annotated

from bson import ObjectId
from fastapi import Depends

from app.api.v1.models.thread import (
    BaseCommentCreateData,
    Comment,
    CommentCreateData,
    CommentUpdateData,
)
from app.api.v1.validators.comment import (
    CommentAuthorValidator,
    CommentByIdValidator,
    CommentCreateValidator,
)
from app.utils.pydantic import ObjectIdAnnotation


class CommentByIdDependency:
    """Comment by identifier dependency."""

    async def __call__(
        self,
        thread_id: Annotated[ObjectId, ObjectIdAnnotation],
        comment_id: Annotated[ObjectId, ObjectIdAnnotation],
        comment_by_id_validator: CommentByIdValidator = Depends(),
    ) -> Comment:
        """Checks comment from request by identifier.

        Args:
            thread_id (Annotated[ObjectId, ObjectIdAnnotation]): BSON object
            identifier of requested thread.
            comment_id (Annotated[ObjectId, ObjectIdAnnotation]): BSON object
            identifier of requested comment.
            comment_by_id_validator (CommentByIdValidator): Comment by identifier
            validator.

        Returns:
            Comment: Comment object.

        """

        return await comment_by_id_validator.validate(
            thread_id=thread_id, comment_id=comment_id
        )


class CommentAuthorDependency:
    """Comment author dependency."""

    async def __call__(
        self,
        thread_id: Annotated[ObjectId, ObjectIdAnnotation],
        comment_id: Annotated[ObjectId, ObjectIdAnnotation],
        comment_author_validator: CommentAuthorValidator = Depends(),
    ) -> Comment:
        """Validates comment author.

        Args:
            thread_id (Annotated[ObjectId, ObjectIdAnnotation]): BSON object
            identifier of requested thread.
            comment_id (Annotated[ObjectId, ObjectIdAnnotation]): BSON object
            identifier of requested comment.
            comment_author_validator (CommentAuthorValidator): Comment author validator.

        Returns:
            Comment: Comment object.

        """

        return await comment_author_validator.validate(
            thread_id=thread_id,
            comment_id=comment_id,
        )


class CommentDataCreateDependency:
    """Comment data create dependency."""

    async def __call__(
        self,
        thread_id: Annotated[ObjectId, ObjectIdAnnotation],
        comment_data: BaseCommentCreateData,
        comment_create_validator: CommentCreateValidator = Depends(),
    ) -> CommentCreateData:
        """Validates data on user create operation.

        Args:
            thread_id (Annotated[ObjectId, ObjectIdAnnotation]): BSON object
            identifier of requested thread.
            comment_data (BaseCommentCreateData): Base comment create data.
            comment_create_validator (CommentCreateValidator): Comment create validator.

        Returns:
            CommentCreateData: Comment create data.

        """

        return await comment_create_validator.validate(
            thread_id=thread_id,
            parent_id=comment_data.parent_comment_id,
            body=comment_data.body,
        )


class CommentDataUpdateDependency:
    """Comment data update dependency."""

    async def __call__(self, comment_data: CommentUpdateData) -> CommentUpdateData:
        """Validates data on user update operation.

        Args:
            comment_data (CommentUpdateData): Comment update data.

        Returns:
            CommentUpdateData: Comment update data.

        """

        return comment_data
