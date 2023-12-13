"""Module that cointains loaders."""

import abc
import os
from typing import Any, Dict, Optional


class BaseLoader(abc.ABC):
    """Base loader."""

    @classmethod
    @abc.abstractmethod
    def load(cls) -> Dict[str, Any]:
        """Abstract method to load data from a source.

        Returns:
            A dictionary containing data loaded from the source,
            where keys are identifiers and values are the data.

        """
        raise NotImplementedError


class EnvironmentLoader(BaseLoader):
    """Environment variables loader."""

    @classmethod
    def load(cls, variable: Optional[str] = None) -> Dict[str, Any]:
        """Loads environment variables.

        Args:
            variable (str, optional): If provided, loads a specific environment
            variable by name. If not provided, loads all environment variables.

        Returns:
            A dictionary containing environment variables, where keys are variable
            names and values are their values.

        Note:
            If `variable` is provided, the function returns a dictionary with a
            single key-value pair.

        """
        if variable is not None:
            return {variable: os.environ.get(variable)}
        return dict(os.environ)
