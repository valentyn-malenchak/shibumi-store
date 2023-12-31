"""Module that contains base service abstract class."""

import abc
from typing import Any, List

from bson import ObjectId


class BaseService(abc.ABC):
    """Base service for encapsulating business logic."""

    @abc.abstractmethod
    async def get_item_by_id(self, id_: ObjectId) -> Any:
        """Retrieves an item by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the item.

        Returns:
            Any: The retrieved item or None if not found.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.

        """
        raise NotImplementedError

    @abc.abstractmethod
    async def create_item(self, item: Any) -> Any:
        """Creates a new item.

        Args:
            item (Any): The data for the new item.

        Returns:
            Any: The ID of created item.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.

        """
        raise NotImplementedError

    @abc.abstractmethod
    async def create_items(self, items: List[Any]) -> List[Any]:
        """Creates new items.

        Args:
            items (List[Any]): The data for the new items.

        Returns:
            List[Any]: The IDs of created items.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.

        """
        raise NotImplementedError

    @abc.abstractmethod
    async def delete_all_items(self) -> None:
        """Deletes all items.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.

        """
        raise NotImplementedError
