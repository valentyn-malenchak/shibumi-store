"""Contains custom meta classes."""

from threading import Lock
from typing import Any, ClassVar


class SingletonMeta(type):
    """Metaclass for creating thread-safe singleton classes."""

    _instances: ClassVar[dict["SingletonMeta", Any]] = {}

    _lock: Lock = Lock()

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        """Creates or returns the existing instance of the class.

        Args:
            cls: The class being instantiated.
            *args (Any): Positional arguments passed to the class constructor.
            **kwargs (Any): Keyword arguments passed to the class constructor.

        Returns:
            Any: The instance of the class.

        """

        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)

                cls._instances[cls] = instance

        return cls._instances[cls]
