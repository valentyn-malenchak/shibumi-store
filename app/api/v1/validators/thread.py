"""Contains thread domain validators."""

from typing import Any

from bson import ObjectId
from fastapi import Depends, HTTPException, Request, status

from app.api.v1.models.thread import Thread
from app.api.v1.services.thread import ThreadService
from app.api.v1.validators import BaseValidator
from app.constants import HTTPErrorMessagesEnum
from app.exceptions import EntityIsNotFoundError


class BaseThreadValidator(BaseValidator):
    """Base thread validator."""

    def __init__(self, request: Request, thread_service: ThreadService = Depends()):
        """Initializes base thread validator.

        Args:
            request (Request): Current request object.
            thread_service (ThreadService): Thread service.

        """

        super().__init__(request=request)

        self.thread_service = thread_service

    async def validate(self, *args: Any) -> Any:
        """Validates data.

        Args:
            args (Any): Method arguments.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.

        """
        raise NotImplementedError


class ThreadByIdValidator(BaseThreadValidator):
    """Thread by identifier validator."""

    async def validate(self, thread_id: ObjectId) -> Thread:
        """Validates requested thread by id.

        Args:
            thread_id (ObjectId): BSON object identifier of requested thread.

        Returns:
            Thread: Thread object.

        Raises:
            HTTPException: If requested thread is not found.

        """

        try:
            thread = await self.thread_service.get_by_id(id_=thread_id)

        except EntityIsNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=HTTPErrorMessagesEnum.ENTITY_IS_NOT_FOUND.format(
                    entity="Thread"
                ),
            )

        return thread
