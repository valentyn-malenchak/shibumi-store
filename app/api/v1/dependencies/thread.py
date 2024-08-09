"""Contains thread domain dependencies."""

from typing import Annotated

from bson import ObjectId
from fastapi import Depends

from app.api.v1.models.thread import Thread, ThreadCreateData
from app.api.v1.validators.thread import ThreadByIdValidator
from app.utils.pydantic import ObjectIdAnnotation


class ThreadByIdDependency:
    """Thread by identifier dependency."""

    async def __call__(
        self,
        thread_id: Annotated[ObjectId, ObjectIdAnnotation],
        thread_by_id_validator: ThreadByIdValidator = Depends(),
    ) -> Thread:
        """Checks thread from request by identifier.

        Args:
            thread_id (Annotated[ObjectId, ObjectIdAnnotation]): BSON object
            identifier of requested thread.
            thread_by_id_validator (ThreadByIdValidator): Thread by identifier
            validator.

        Returns:
            Thread: Thread object.

        """

        return await thread_by_id_validator.validate(thread_id=thread_id)


class ThreadDataCreateDependency:
    """Thread data create dependency."""

    async def __call__(
        self,
        thread_data: ThreadCreateData,
    ) -> ThreadCreateData:
        """Validates data on thread create operation.

        Args:
            thread_data (ThreadCreateData): Thread create data.

        Returns:
            ThreadCreateData: Thread create data.

        """

        return thread_data
