"""Contains comment domain dependencies."""

from typing import Annotated

from bson import ObjectId
from fastapi import Depends

from app.api.v1.models.comment import (
    BaseCommentCreateData,
    Comment,
    CommentCreateData,
)
from app.api.v1.validators.comment import (
    CommentAccessValidator,
    CommentByIdValidator,
    CommentCreateValidator,
)
from app.utils.pydantic import ObjectIdAnnotation


class CommentByIdDependency:
    """Comment by identifier dependency."""

    async def __call__(
        self,
        comment_id: Annotated[ObjectId, ObjectIdAnnotation],
        comment_by_id_validator: CommentByIdValidator = Depends(),
    ) -> Comment:
        """Validates comment from request by identifier.

        Args:
            comment_id (Annotated[ObjectId, ObjectIdAnnotation]): BSON object
            identifier of requested comment.
            comment_by_id_validator (CommentByIdValidator): Comment by identifier
            validator.

        Returns:
            Comment: Comment object.

        """

        return await comment_by_id_validator.validate(comment_id=comment_id)


class CommentAccessDependency:
    """Comment access dependency."""

    async def __call__(
        self,
        comment_id: Annotated[ObjectId, ObjectIdAnnotation],
        comment_access_validator: CommentAccessValidator = Depends(),
    ) -> Comment:
        """Validates user access to comment.

        Args:
            comment_id (Annotated[ObjectId, ObjectIdAnnotation]): BSON object
            identifier of requested comment.
            comment_access_validator (CommentAccessValidator): Comment access validator.

        Returns:
            Comment: Comment object.

        """

        return await comment_access_validator.validate(comment_id=comment_id)


class CommentDataCreateDependency:
    """Comment data create dependency."""

    async def __call__(
        self,
        comment_data: BaseCommentCreateData,
        comment_create_validator: CommentCreateValidator = Depends(),
    ) -> CommentCreateData:
        """Validates data on comment create operation.

        Args:
            comment_data (BaseCommentCreateData): Base comment create data.
            comment_create_validator (CommentCreateValidator): Comment create validator.

        Returns:
            CommentCreateData: Comment create data.

        """

        return await comment_create_validator.validate(
            thread_id=comment_data.thread_id,
            parent_id=comment_data.parent_comment_id,
            body=comment_data.body,
        )
