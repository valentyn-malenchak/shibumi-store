"""Module that contains loaders."""

import abc
import json
import os
from typing import Any, Dict

from app.utils.json import JSONDecoder


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

    def load(self) -> Dict[str, Any]:
        """Loads environment variables.

        Returns:
            Dict[str, Any]: A dictionary containing environment variables,
            where keys are variable names and values are their values.

        Note:
            If `variable` is provided, the function returns a dictionary with a
            single key-value pair.

        """
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
            return json.load(json_file, cls=JSONDecoder)
