"""Module that contains role-scopes service class."""


from typing import Any, List

from bson import ObjectId
from fastapi import BackgroundTasks, Depends

from app.api.v1.models import PaginationModel, SearchModel, SortingModel
from app.api.v1.repositories.role_scopes import RoleScopesRepository
from app.api.v1.services import BaseService
from app.services.mongo.transaction_manager import TransactionManager
from app.services.redis.service import RedisService


class RoleScopesService(BaseService):
    """Role-scopes service for encapsulating business logic."""

    def __init__(
        self,
        background_tasks: BackgroundTasks,
        repository: RoleScopesRepository = Depends(),
        redis_service: RedisService = Depends(),
        transaction_manager: TransactionManager = Depends(),
    ) -> None:
        """Initializes the role-scopes service.

        Args:
            background_tasks (BackgroundTasks): Background tasks.
            repository (RoleScopesRepository): An instance of the Role-Scopes
            repository.
            redis_service (RedisService): Redis service.
            transaction_manager (TransactionManager): Transaction manager.

        """

        super().__init__(
            background_tasks=background_tasks,
            redis_service=redis_service,
            transaction_manager=transaction_manager,
        )

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
