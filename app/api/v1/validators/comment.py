"""Contains message domain validators."""

from typing import Any

from bson import ObjectId
from fastapi import Depends, HTTPException, Request, status

from app.api.v1.models.thread import Comment, CommentCreateData
from app.api.v1.services.comment import CommentService
from app.api.v1.validators import BaseValidator
from app.api.v1.validators.thread import ThreadByIdValidator
from app.constants import HTTPErrorMessagesEnum
from app.exceptions import EntityIsNotFoundError


class BaseCommentValidator(BaseValidator):
    """Base comment validator."""

    def __init__(self, request: Request, comment_service: CommentService = Depends()):
        """Initializes base comment validator.

        Args:
            request (Request): Current request object.
            comment_service (CommentService): Comment service.

        """

        super().__init__(request=request)

        self.comment_service = comment_service

    async def validate(self, *args: Any) -> Any:
        """Validates data.

        Args:
            args (Any): Method arguments.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.

        """
        raise NotImplementedError


class CommentByIdValidator(BaseCommentValidator):
    """Comment by identifier validator."""

    async def validate(self, comment_id: ObjectId) -> Comment:
        """Validates requested comment by id.

        Args:
            comment_id (ObjectId): BSON object identifier of requested comment.

        Returns:
            Comment: Comment object.

        Raises:
            HTTPException: If requested comment is not found.

        """

        try:
            comment = await self.comment_service.get_by_id(id_=comment_id)

        except EntityIsNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=HTTPErrorMessagesEnum.ENTITY_IS_NOT_FOUND.format(
                    entity="Comment"
                ),
            )

        return comment


class CommentCreateValidator(BaseCommentValidator):
    """Comment create validator."""

    def __init__(
        self,
        request: Request,
        comment_service: CommentService = Depends(),
        thread_by_id_validator: ThreadByIdValidator = Depends(),
        comment_by_id_validator: CommentByIdValidator = Depends(),
    ) -> None:
        """Initializes comment create validator.

        Args:
            request (Request): Current request object.
            comment_service (CommentService): Comment service.
            thread_by_id_validator (ThreadByIdValidator): Thread by id validator.
            comment_by_id_validator (CommentByIdValidator): Comment by id validator.

        """

        super().__init__(request=request, comment_service=comment_service)

        self.thread_by_id_validator = thread_by_id_validator

        self.comment_by_id_validator = comment_by_id_validator

    async def validate(
        self, thread_id: ObjectId, parent_id: ObjectId | None, body: str
    ) -> CommentCreateData:
        """Checks if thread comment can be created.

        Args:
            thread_id (ObjectId): BSON object identifier of requested thread.
            parent_id (ObjectId | None): BSON object identifier of requested
            parent comment or None.
            body (str): Comment body.

        Returns:
            CommentCreateData: Comment create data.

        """

        await self.thread_by_id_validator.validate(thread_id=thread_id)

        parent_comment = (
            await self.comment_by_id_validator.validate(comment_id=parent_id)
            if parent_id is not None
            else None
        )

        return CommentCreateData(
            body=body,
            author_id=self.request.state.current_user.object.id,
            thread_id=thread_id,
            parent_comment=parent_comment,
        )
