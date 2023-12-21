"""Contains custom meta classes."""

from typing import Any, Dict


class SingletonMeta(type):
    """
    Metaclass for creating singleton classes.
    Ensures that only one instance of a class is ever created.
    """

    _instances: Dict["SingletonMeta", "SingletonMeta"] = {}

    def __call__(cls, *args: Any, **kwargs: Any) -> "SingletonMeta":
        """Creates or returns the existing instance of the class.

        Args:
            cls: The class being instantiated.
            *args (Any): Positional arguments passed to the class constructor.
            **kwargs (Any): Keyword arguments passed to the class constructor.

        Returns:
            SingletonClass: The instance of the class.

        """

        if cls not in cls._instances:
            instance: "SingletonMeta" = super().__call__(*args, **kwargs)

            cls._instances[cls] = instance

        return cls._instances[cls]
