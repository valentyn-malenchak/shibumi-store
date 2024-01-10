"""Contains common domain validator classes."""

import abc
from typing import Any

from fastapi import Request


class BaseValidator(abc.ABC):
    """Base validator."""

    def __init__(self, request: Request):
        """Initializes base user validator.

        Args:
            request (Request): Current request object.

        """
        self.request = request

    @abc.abstractmethod
    async def validate(self, *args: Any) -> Any:
        """Validates data.

        Args:
            args (Any): Method arguments.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.

        """
        raise NotImplementedError
