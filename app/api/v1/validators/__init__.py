"""Contains common domain validator classes.

Validator rules:

- Validates concrete chunk of HTTP request data.
- Recommended name format: {Entity}{Operation}Validator.
- Should use entity services or other validators.
- In general it is not recommended to make "chain" validators, if possible it is
better to implement this on dependencies level.

"""

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
