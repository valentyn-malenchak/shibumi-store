"""Module that contains role service class."""

from collections.abc import Mapping
from typing import Any

from bson import ObjectId, json_util
from fastapi import BackgroundTasks, Depends

from app.api.v1.constants import RolesEnum
from app.api.v1.repositories.role import RoleRepository
from app.api.v1.services import BaseService
from app.services.mongo.transaction_manager import TransactionManager
from app.services.redis.constants import RedisNamesEnum, RedisNamesTTLEnum
from app.services.redis.service import RedisService


class RoleService(BaseService):
    """Role service for encapsulating business logic."""

    def __init__(
        self,
        background_tasks: BackgroundTasks,
        redis_service: RedisService = Depends(),
        transaction_manager: TransactionManager = Depends(),
        repository: RoleRepository = Depends(),
    ) -> None:
        """Initializes the role service.

        Args:
            background_tasks (BackgroundTasks): Background tasks.
            redis_service (RedisService): Redis service.
            transaction_manager (TransactionManager): Transaction manager.
            repository (RoleRepository): An instance of the Role repository.

        """

        super().__init__(
            background_tasks=background_tasks,
            redis_service=redis_service,
            transaction_manager=transaction_manager,
        )

        self.repository = repository

    async def get(self, **kwargs: Any) -> list[Mapping[str, Any]]:
        """Retrieves a list of roles based on parameters.

        Args:
            kwargs (Any): Keyword parameters.

        Returns:
            list[Mapping[str, Any]]: The retrieved list of roles.

        """

        cached_roles = await self.redis_service.get(name=RedisNamesEnum.ROLES_LIST)

        if cached_roles is not None:
            return json_util.loads(cached_roles)  # type: ignore

        roles = await self.repository.get()

        await self.redis_service.set(
            name=RedisNamesEnum.ROLES_LIST,
            value=json_util.dumps(roles),
            ttl=RedisNamesTTLEnum.ROLES_LIST.value,
        )

        return roles

    async def count(self, **kwargs: Any) -> int:
        """Counts roles based on parameters.

        Args:
            kwargs (Any): Keyword parameters.

        Returns:
            int: Count of roles.

        """

        cached_roles = await self.redis_service.get(name=RedisNamesEnum.ROLES_LIST)

        if cached_roles is not None:
            return len(json_util.loads(cached_roles))

        return await self.repository.count()

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

    async def create(self, data: Any) -> Any:
        """Creates a new role.

        Args:
            data (Any): The data for the new role.

        Returns:
            Any: Created role.

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

    async def delete(self, item: Any) -> None:
        """Deletes a role.

        Args:
            item (Any): Role object.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def get_scopes_by_roles(self, roles: list[RolesEnum]) -> list[str]:
        """Retrieves a list of scopes from the repository by roles name list.

        Args:
            roles (list[str]): List of roles.

        Returns:
            list[str]: The retrieved scopes.

        """
        return await self.repository.get_scopes_by_roles(roles=roles)
