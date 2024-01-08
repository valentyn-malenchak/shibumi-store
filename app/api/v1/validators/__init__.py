"""Contains common domain validator classes."""

import abc
from typing import Any

from bson import ObjectId
from fastapi import HTTPException, status

from app.constants import HTTPErrorMessagesEnum


class BaseValidator(abc.ABC):
    """Base validator."""

    @classmethod
    @abc.abstractmethod
    def validate(cls, *args: Any) -> Any:
        """Validates data.

        Args:
            *args (Any): Method arguments.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.

        """
        raise NotImplementedError


class ObjectIDValidator(abc.ABC):
    """Object ID validator."""

    @classmethod
    def validate(cls, id_: str) -> ObjectId:
        """Validates BSON object id.

        Args:
            id_ (str): String identifier.

        Returns:
            ObjectId: BSON object identifier.

        Raises:
            HTTPException: If object identifier is invalid.

        """

        if not ObjectId.is_valid(id_):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=HTTPErrorMessagesEnum.INVALID_IDENTIFIER.value,
            )

        return ObjectId(id_)
