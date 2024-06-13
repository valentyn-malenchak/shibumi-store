"""Contains comment domain dependencies."""

from typing import Annotated

from bson import ObjectId
from fastapi import Depends

from app.api.v1.models.thread import BaseCommentCreateData, CommentCreateData
from app.api.v1.validators.comment import CommentCreateValidator
from app.utils.pydantic import ObjectIdAnnotation


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
