"""Module that contains user service abstract class."""


import arrow
from bson import ObjectId
from fastapi import Depends, HTTPException, status
from pymongo.errors import DuplicateKeyError

from app.api.v1.auth.password import Password
from app.api.v1.models.user import CreateUserRequestModel, UpdateUserRequestModel, User
from app.api.v1.repositories.user import UserRepository
from app.api.v1.services import BaseService
from app.constants import HTTPErrorMessagesEnum


class UserService(BaseService):
    """User service for encapsulating business logic."""

    def __init__(self, repository: UserRepository = Depends()) -> None:
        """Initializes the UserService.

        This method sets up the MongoDB service instance for data access.

        Args:
            repository (UserRepository): An instance of the User repository.

        """

        self.repository = repository

    async def get_item_by_id(self, id_: ObjectId) -> User | None:
        """Retrieves an item by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the item.

        Returns:
            User | None: User object or None.

        """
        return await self.repository.get_item_by_id(id_=id_)

    async def get_item_by_username(self, username: str) -> User | None:
        """Retrieves an item by its username.

        Args:
            username (str): Username.

        Returns:
            User | None: User object or None.

        """
        return await self.repository.get_item_by_username(username=username)

    async def create_item(self, item: CreateUserRequestModel) -> User | None:
        """Creates a new user.

        Args:
            item (CreateUserRequestModel): The data for the new user.

        Returns:
            User | None: The created user.

        """

        password = Password.get_password_hash(password=item.password)

        try:
            id_ = await self.repository.create_item(
                item={
                    # Replaces plain password on hashed one
                    **item.model_dump(exclude={"password", "roles"}),
                    "hashed_password": password,
                    "birthdate": arrow.get(item.birthdate).datetime,
                    "roles": [role.name for role in item.roles],
                    "deleted": False,
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
            )

        except DuplicateKeyError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=HTTPErrorMessagesEnum.ENTITY_FIELD_UNIQUENESS.value.format(
                    entity="User", field="username"
                ),
            )

        return await self.get_item_by_id(id_=id_)

    async def update_item_by_id(
        self, id_: ObjectId, item: UpdateUserRequestModel
    ) -> User | None:
        """Updates an item by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the user.
            item (Any): Data to update user.

        Returns:
            User | None: The updated user.

        """

        password = Password.get_password_hash(password=item.password)

        await self.repository.update_item_by_id(
            id_=id_,
            item={
                # Replaces plain password on hashed one
                **item.model_dump(exclude={"password", "roles"}),
                "hashed_password": password,
                "roles": [role.name for role in item.roles],
                "birthdate": arrow.get(item.birthdate).datetime,
                "updated_at": arrow.utcnow().datetime,
            },
        )

        return await self.get_item_by_id(id_=id_)

    async def delete_item_by_id(self, id_: ObjectId) -> None:
        """Softly deletes a user by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the user.

        """

        await self.repository.update_item_by_id(
            id_=id_, item={"deleted": True, "updated_at": arrow.utcnow().datetime}
        )
