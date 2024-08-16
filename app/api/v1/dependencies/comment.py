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
    CommentByIdValidator,
    CommentDeleteAccessValidator,
    CommentStatusValidator,
    CommentUpdateAccessValidator,
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


class CommentByIdStatusGetDependency(metaclass=SingletonMeta):
    """Comment by identifier status get dependency."""

    async def __call__(
        self,
        comment: Comment = Depends(CommentByIdGetDependency()),
        comment_status_validator: CommentStatusValidator = Depends(),
    ) -> Comment:
        """Validates comment status from request by identifier.

        Args:
            comment (Comment): Comment object.
            comment_status_validator (CommentStatusValidator): Comment status validator.

        Returns:
            Comment: Comment object.

        """
        return await comment_status_validator.validate(comment=comment)


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


class CommentUpdateAccessDependency(metaclass=SingletonMeta):
    """Comment update access dependency."""

    async def __call__(
        self,
        comment: Comment = Depends(CommentByIdStatusGetDependency()),
        comment_update_access_validator: CommentUpdateAccessValidator = Depends(),
    ) -> Comment:
        """Validates access to specific comment on update operation.

        Args:
            comment (Comment): Comment object.
            comment_update_access_validator (CommentUpdateAccessValidator): Comment
            update access validator.

        Returns:
            Comment: Comment object.

        """
        return await comment_update_access_validator.validate(comment=comment)


class CommentDeleteAccessDependency(metaclass=SingletonMeta):
    """Comment delete access dependency."""

    async def __call__(
        self,
        comment: Comment = Depends(CommentByIdStatusGetDependency()),
        comment_delete_access_validator: CommentDeleteAccessValidator = Depends(),
    ) -> Comment:
        """Validates access to specific comment on delete operation.

        Args:
            comment (Comment): Comment object.
            comment_delete_access_validator (CommentDeleteAccessValidator): Comment
            delete access validator.

        Returns:
            Comment: Comment object.

        """
        return await comment_delete_access_validator.validate(comment=comment)
