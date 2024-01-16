"""Module that contains role-scopes service abstract class."""


from typing import Any, List

from bson import ObjectId
from fastapi import Depends

from app.api.v1.models import PaginationModel, SearchModel, SortingModel
from app.api.v1.repositories.role_scopes import RoleScopesRepository
from app.api.v1.services import BaseService


class RoleScopesService(BaseService):
    """Role-scopes service for encapsulating business logic."""

    def __init__(self, repository: RoleScopesRepository = Depends()) -> None:
        """Initializes the role-scopes service.

        This method sets up the MongoDB service instance for data access.

        Args:
            repository (RoleScopesRepository): An instance of the User repository.

        """

        self.repository = repository

    async def get(
        self,
        filter_: Any,
        search: SearchModel,
        sorting: SortingModel,
        pagination: PaginationModel,
    ) -> List[Any]:
        """Retrieves a list of roles-scopes based on parameters.

        Args:
            filter_ (Any): Parameters for list filtering.
            search (SearchModel): Parameters for list searching.
            sorting (SortingModel): Parameters for sorting.
            pagination (PaginationModel): Parameters for pagination.

        Returns:
            List[Any]: The retrieved list of roles-scopes.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def count(self, filter_: Any, search: SearchModel) -> int:
        """Counts documents based on parameters.

        Args:
            filter_ (Any): Parameters for list filtering.
            search (SearchModel): Parameters for list searching.

        Returns:
            int: Count of documents.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def get_by_id(self, id_: ObjectId) -> Any:
        """Retrieves a role-scopes by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the role-scopes.

        Returns:
            Any: The retrieved role-scopes or None if not found.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def get_scopes_by_roles(self, roles: List[str]) -> List[str]:
        """Retrieves a list of scopes from the repository by roles name list.

        Args:
            roles (List[str]): List of roles.

        Returns:
            List[str]: The retrieved scopes.

        """
        return await self.repository.get_scopes_by_roles(roles=roles)

    async def create(self, item: Any) -> Any:
        """Creates a new role-scopes.

        Args:
            item (Any): The data for the new role-scopes.

        Returns:
            Any: The ID of created role-scopes.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def update_by_id(self, id_: ObjectId, item: Any) -> Any:
        """Updates a role-scopes by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the role-scopes.
            item (Any): Data to update role-scopes.

        Returns:
            Any: The updated role-scopes.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def delete_by_id(self, id_: ObjectId) -> None:
        """Deletes a role-scopes by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the role-scopes.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError
