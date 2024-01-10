"""Contains common domain validator classes."""

import abc
from typing import Any


class BaseValidator(abc.ABC):
    """Base validator."""

    @classmethod
    @abc.abstractmethod
    def validate(cls, *args: Any) -> Any:
        """Validates data.

        Args:
            args (Any): Method arguments.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.

        """
        raise NotImplementedError
