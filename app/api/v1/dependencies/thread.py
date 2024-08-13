"""Contains thread domain dependencies."""

from typing import Annotated

from bson import ObjectId
from fastapi import Depends

from app.api.v1.models.thread import (
    Thread,
)
from app.api.v1.validators.thread import ThreadByIdValidator
from app.utils.metas import SingletonMeta
from app.utils.pydantic import ObjectIdAnnotation


class ThreadByIdGetDependency(metaclass=SingletonMeta):
    """Thread by identifier get dependency."""

    async def __call__(
        self,
        thread_id: Annotated[ObjectId, ObjectIdAnnotation],
        thread_by_id_validator: ThreadByIdValidator = Depends(),
    ) -> Thread:
        """Validates thread by its unique identifier.

        Args:
            thread_id (Annotated[ObjectId, ObjectIdAnnotation]): BSON object
            identifier of requested thread.
            thread_by_id_validator (ThreadByIdValidator): Thread by identifier
            validator.

        Returns:
            Thread: Thread object.

        """
        return await thread_by_id_validator.validate(thread_id=thread_id)
