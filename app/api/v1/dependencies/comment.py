"""Contains comment domain dependencies."""

from typing import Annotated

from bson import ObjectId
from fastapi import Depends

from app.api.v1.models.comment import (
    BaseCommentCreateData,
    Comment,
    CommentCreateData,
    CommentUpdateData,
)
from app.api.v1.validators.comment import (
    CommentByIdValidator,
    CommentCreateValidator,
    CommentUserValidator,
)
from app.utils.pydantic import ObjectIdAnnotation


class CommentByIdDependency:
    """Comment by identifier dependency."""

    async def __call__(
        self,
        comment_id: Annotated[ObjectId, ObjectIdAnnotation],
        comment_by_id_validator: CommentByIdValidator = Depends(),
    ) -> Comment:
        """Checks comment from request by identifier.

        Args:
            comment_id (Annotated[ObjectId, ObjectIdAnnotation]): BSON object
            identifier of requested comment.
            comment_by_id_validator (CommentByIdValidator): Comment by identifier
            validator.

        Returns:
            Comment: Comment object.

        """

        return await comment_by_id_validator.validate(comment_id=comment_id)


class CommentUserDependency:
    """Comment user dependency."""

    async def __call__(
        self,
        comment_id: Annotated[ObjectId, ObjectIdAnnotation],
        comment_user_validator: CommentUserValidator = Depends(),
    ) -> Comment:
        """Validates comment user.

        Args:
            comment_id (Annotated[ObjectId, ObjectIdAnnotation]): BSON object
            identifier of requested comment.
            comment_user_validator (CommentUserValidator): Comment user validator.

        Returns:
            Comment: Comment object.

        """

        return await comment_user_validator.validate(comment_id=comment_id)


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


class CommentDataUpdateDependency:
    """Comment data update dependency."""

    async def __call__(self, comment_data: CommentUpdateData) -> CommentUpdateData:
        """Validates data on comment update operation.

        Args:
            comment_data (CommentUpdateData): Comment update data.

        Returns:
            CommentUpdateData: Comment update data.

        """

        return comment_data
