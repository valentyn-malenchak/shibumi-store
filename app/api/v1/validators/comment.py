"""Contains comment domain validators."""

from typing import Any

from bson import ObjectId
from fastapi import Depends, HTTPException, Request, status

from app.api.v1.models.comment import Comment
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
        """Validates requested comment by identifier.

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


class CommentStatusValidator(BaseCommentValidator):
    """Comment status validator."""

    async def validate(self, comment: Comment) -> Comment:
        """Validates if requested comment is deleted.

        Args:
            comment (Comment): Comment object.

        Returns:
            Comment: Comment object.

        Raises:
            HTTPException: If requested comment is deleted.

        """

        if comment.deleted is True:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=HTTPErrorMessagesEnum.ENTITY_IS_NOT_FOUND.format(
                    entity="Comment"
                ),
            )

        return comment


class ParentCommentValidator(BaseCommentValidator):
    """Parent comment validator."""

    def __init__(
        self,
        request: Request,
        comment_service: CommentService = Depends(),
        thread_by_id_validator: ThreadByIdValidator = Depends(),
        comment_by_id_validator: CommentByIdValidator = Depends(),
    ) -> None:
        """Initializes parent comment validator.

        Args:
            request (Request): Current request object.
            comment_service (CommentService): Comment service.
            thread_by_id_validator (ThreadByIdValidator): Thread by identifier
            validator.
            comment_by_id_validator (CommentByIdValidator): Comment by identifier
            validator.

        """

        super().__init__(request=request, comment_service=comment_service)

        self.thread_by_id_validator = thread_by_id_validator

        self.comment_by_id_validator = comment_by_id_validator

    async def validate(
        self, thread_id: ObjectId, parent_comment_id: ObjectId | None
    ) -> Comment | None:
        """Validates parent comment.

        Args:
            thread_id (ObjectId): BSON object identifier of requested thread.
            parent_comment_id (ObjectId | None): BSON object identifier of requested
            parent comment or None.

        Returns:
            Comment | None: Parent comment object or None.

        """

        # Validates thread
        thread = await self.thread_by_id_validator.validate(thread_id=thread_id)

        if parent_comment_id is not None:
            # Validates parent comment if it is set
            parent_comment = await self.comment_by_id_validator.validate(
                comment_id=parent_comment_id
            )

            # Check if parent comment belongs to thread
            if parent_comment.thread_id != thread.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=HTTPErrorMessagesEnum.ENTITIES_ARE_NOT_RELATED.format(
                        child_entity="Comment", parent_entity="thread"
                    ),
                )

        else:
            parent_comment = None

        return parent_comment


class CommentUpdateAccessValidator(BaseCommentValidator):
    """Comment update access validator."""

    async def validate(self, comment: Comment) -> Comment:
        """Validates if user has access to update comment.

        Args:
            comment (Comment): Comment object.

        Returns:
            Comment: Comment object.

        Raises:
            HTTPException: If current user is not related to comment.

        """

        current_user = self.request.state.current_user

        if comment.user_id != current_user.object.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=HTTPErrorMessagesEnum.ACCESS_DENIED.format(
                    destination="comment"
                ),
            )

        return comment


class CommentDeleteAccessValidator(BaseCommentValidator):
    """Comment delete access validator."""

    def __init__(
        self,
        request: Request,
        comment_service: CommentService = Depends(),
        comment_update_access_validator: CommentUpdateAccessValidator = Depends(),
    ) -> None:
        """Initializes comment delete access validator.

        Args:
            request (Request): Current request object.
            comment_service (CommentService): Comment service.
            comment_update_access_validator (CommentUpdateAccessValidator): Comment
            update access validator.

        """

        super().__init__(request=request, comment_service=comment_service)

        self.comment_update_access_validator = comment_update_access_validator

    async def validate(self, comment: Comment) -> Comment:
        """Validates if user has access to delete comment.

        Args:
            comment (Comment): Comment object.

        Returns:
            Comment: Comment object.

        Raises:
            HTTPException: If current user does not have access to delete comment.

        """

        current_user = self.request.state.current_user

        if current_user.object.is_client is True:
            await self.comment_update_access_validator.validate(comment=comment)

        return comment
