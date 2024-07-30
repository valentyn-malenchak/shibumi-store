"""Contains comment domain validators."""

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

    def __init__(
        self,
        request: Request,
        comment_service: CommentService = Depends(),
        thread_by_id_validator: ThreadByIdValidator = Depends(),
    ) -> None:
        """Initializes comment by identifier validator.

        Args:
            request (Request): Current request object.
            comment_service (CommentService): Comment service.
            thread_by_id_validator (ThreadByIdValidator): Thread by id validator.

        """

        super().__init__(request=request, comment_service=comment_service)

        self.thread_by_id_validator = thread_by_id_validator

    async def validate(self, thread_id: ObjectId, comment_id: ObjectId) -> Comment:
        """Validates requested comment by id.

        Args:
            thread_id (ObjectId): BSON object identifier of requested thread.
            comment_id (ObjectId): BSON object identifier of requested comment.

        Returns:
            Comment: Comment object.

        Raises:
            HTTPException: If requested comment is not found or comment does not
            belong to thread.

        """

        thread = await self.thread_by_id_validator.validate(thread_id=thread_id)

        try:
            comment = await self.comment_service.get_by_id(id_=comment_id)

        except EntityIsNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=HTTPErrorMessagesEnum.ENTITY_IS_NOT_FOUND.format(
                    entity="Comment"
                ),
            )

        # Check if comment belongs to thread
        if comment.thread_id != thread.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=HTTPErrorMessagesEnum.ENTITIES_ARE_NOT_RELATED.format(
                    child_entity="Comment", parent_entity="thread"
                ),
            )

        return comment


class CommentUserValidator(BaseCommentValidator):
    """Comment user validator."""

    def __init__(
        self,
        request: Request,
        comment_service: CommentService = Depends(),
        comment_by_id_validator: CommentByIdValidator = Depends(),
    ) -> None:
        """Initializes comment user validator.

        Args:
            request (Request): Current request object.
            comment_service (CommentService): Comment service.
            comment_by_id_validator (CommentByIdValidator): Comment by id validator.

        """

        super().__init__(request=request, comment_service=comment_service)

        self.comment_by_id_validator = comment_by_id_validator

    async def validate(self, thread_id: ObjectId, comment_id: ObjectId) -> Comment:
        """Validates requested comment user.

        Args:
            thread_id (ObjectId): BSON object identifier of requested thread.
            comment_id (ObjectId): BSON object identifier of requested comment.

        Returns:
            Comment: Comment object.

        Raises:
            HTTPException: If current user is not related to comment.

        """

        comment = await self.comment_by_id_validator.validate(
            thread_id=thread_id, comment_id=comment_id
        )

        current_user = self.request.state.current_user

        if comment.user_id != current_user.object.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=HTTPErrorMessagesEnum.COMMENT_ACCESS_DENIED,
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

        if parent_id is not None:
            # Validates thread and parent comment if it is set
            parent_comment = await self.comment_by_id_validator.validate(
                thread_id=thread_id, comment_id=parent_id
            )
        else:
            # Otherwise just validates thread
            await self.thread_by_id_validator.validate(thread_id=thread_id)

            parent_comment = None

        return CommentCreateData(
            body=body,
            user_id=self.request.state.current_user.object.id,
            thread_id=thread_id,
            parent_comment=parent_comment,
        )
