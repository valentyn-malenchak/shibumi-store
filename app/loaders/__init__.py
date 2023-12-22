"""Module that contains loaders."""

import abc
import json
import os
from typing import Any, Dict


class BaseLoader(abc.ABC):
    """Base loader."""

    @abc.abstractmethod
    def load(self) -> Dict[str, Any]:
        """Abstract method to load data from a source.

        Returns:
            Dict[str, Any]: A dictionary containing data loaded from the source,
            where keys are identifiers and values are the data.

        """
        raise NotImplementedError


class EnvironmentLoader(BaseLoader):
    """Environment variables loader."""

    def load(self, variable: str | None = None) -> Dict[str, Any]:
        """Loads environment variables.

        Args:
            variable (str | None): If provided, loads a specific environment
            variable by name. If not provided, loads all environment variables.

        Returns:
            Dict[str, Any]: A dictionary containing environment variables,
            where keys are variable names and values are their values.

        Note:
            If `variable` is provided, the function returns a dictionary with a
            single key-value pair.

        """
        if variable is not None:
            return {variable: os.environ.get(variable)}
        return dict(os.environ)


class JSONFileLoader(BaseLoader):
    """JSON file loader."""

    def __init__(self, file_path: str) -> None:
        """JSON file loader initialization method.

        Args:
            file_path (str): Path to JSON file.

        """

        super().__init__()

        self.file_path = file_path

    def load(self) -> Any:
        """Loads environment variables.

        Returns:
            Any: JSON content.

        """

        path = os.path.join(os.getcwd(), self.file_path)

        with open(path) as json_file:
            return json.load(json_file)
