"""Contains comment domain dependencies."""

from typing import Annotated

from bson import ObjectId
from fastapi import Depends, Request

from app.api.v1.models.comment import (
    BaseCommentCreateData,
    Comment,
    CommentCreateData,
)
from app.api.v1.validators.comment import (
    CommentAccessValidator,
    CommentByIdValidator,
    ParentCommentValidator,
)
from app.utils.metas import SingletonMeta
from app.utils.pydantic import ObjectIdAnnotation


class CommentByIdGetDependency(metaclass=SingletonMeta):
    """Comment by identifier get dependency."""

    async def __call__(
        self,
        comment_id: Annotated[ObjectId, ObjectIdAnnotation],
        comment_by_id_validator: CommentByIdValidator = Depends(),
    ) -> Comment:
        """Validates comment by its unique identifier.

        Args:
            comment_id (Annotated[ObjectId, ObjectIdAnnotation]): BSON object
            identifier of requested comment.
            comment_by_id_validator (CommentByIdValidator): Comment by identifier
            validator.

        Returns:
            Comment: Comment object.

        """
        return await comment_by_id_validator.validate(comment_id=comment_id)


class CommentByIdGetAccessDependency(metaclass=SingletonMeta):
    """Comment by identifier get access dependency."""

    async def __call__(
        self,
        comment: Comment = Depends(CommentByIdGetDependency()),
        comment_access_validator: CommentAccessValidator = Depends(),
    ) -> Comment:
        """Validates access to specific comment.

        Args:
            comment (Comment): Comment object.
            comment_access_validator (CommentAccessValidator): Comment access validator.

        Returns:
            Comment: Comment object.

        """
        return await comment_access_validator.validate(comment=comment)


class CommentDataCreateDependency(metaclass=SingletonMeta):
    """Comment data create dependency."""

    async def __call__(
        self,
        request: Request,
        comment_data: BaseCommentCreateData,
        parent_comment_validator: ParentCommentValidator = Depends(),
    ) -> CommentCreateData:
        """Validates data on comment create operation.

        Args:
            request (Request): Current request object.
            comment_data (BaseCommentCreateData): Base comment create data.
            parent_comment_validator (ParentCommentValidator): Parent comment validator.

        Returns:
            CommentCreateData: Comment create data.

        """

        parent_comment = await parent_comment_validator.validate(
            thread_id=comment_data.thread_id,
            parent_comment_id=comment_data.parent_comment_id,
        )

        return CommentCreateData(
            body=comment_data.body,
            user_id=request.state.current_user.object.id,
            thread_id=comment_data.thread_id,
            parent_comment=parent_comment,
        )
