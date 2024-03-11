"""Module that contains role service class."""


from typing import Any, List

from bson import ObjectId
from fastapi import BackgroundTasks, Depends

from app.api.v1.constants import RolesEnum
from app.api.v1.models import PaginationModel, SearchModel, SortingModel
from app.api.v1.repositories.role import RoleRepository
from app.api.v1.services import BaseService
from app.services.mongo.transaction_manager import TransactionManager
from app.services.redis.service import RedisService


class RoleService(BaseService):
    """Role service for encapsulating business logic."""

    def __init__(
        self,
        background_tasks: BackgroundTasks,
        repository: RoleRepository = Depends(),
        redis_service: RedisService = Depends(),
        transaction_manager: TransactionManager = Depends(),
    ) -> None:
        """Initializes the role service.

        Args:
            background_tasks (BackgroundTasks): Background tasks.
            repository (RoleRepository): An instance of the Role repository.
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
        """Retrieves a list of roles based on parameters.

        Args:
            filter_ (Any): Parameters for list filtering.
            search (SearchModel): Parameters for list searching.
            sorting (SortingModel): Parameters for sorting.
            pagination (PaginationModel): Parameters for pagination.

        Returns:
            List[Any]: The retrieved list of roles.

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
        """Retrieves a role by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the role.

        Returns:
            Any: The retrieved role or None if not found.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def get_scopes_by_roles(self, roles: List[RolesEnum]) -> List[str]:
        """Retrieves a list of scopes from the repository by roles name list.

        Args:
            roles (List[str]): List of roles.

        Returns:
            List[str]: The retrieved scopes.

        """
        return await self.repository.get_scopes_by_roles(roles=roles)

    async def create(self, data: Any) -> Any:
        """Creates a new role.

        Args:
            data (Any): The data for the new role.

        Returns:
            Any: The ID of created role.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def update(self, item: Any, data: Any) -> Any:
        """Updates a role object.

        Args:
            item (Any): Role object.
            data (Any): Data to update role.

        Returns:
            Any: The updated role.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def update_by_id(self, id_: ObjectId, data: Any) -> Any:
        """Updates a role by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the role.
            data (Any): Data to update role.

        Returns:
            Any: The updated role.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def delete_by_id(self, id_: ObjectId) -> None:
        """Deletes a role by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the role.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError
