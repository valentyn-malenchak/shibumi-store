"""Module that contains base service abstract class."""

import abc


class BaseService(abc.ABC):
    """Base service abstract class."""

    _name: str | None = None

    @classmethod
    @abc.abstractmethod
    def on_startup(cls) -> None:
        """Runs on application startup."""
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def on_shutdown(cls) -> None:
        """Runs on application shutdown."""
        raise NotImplementedError
