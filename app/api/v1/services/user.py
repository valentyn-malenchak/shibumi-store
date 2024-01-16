"""Module that contains user service abstract class."""


import hashlib
import secrets
from typing import Any, List, Mapping

import arrow
from bson import ObjectId
from fastapi import Depends, HTTPException, status
from pymongo.errors import DuplicateKeyError

from app.api.v1.auth.password import Password
from app.api.v1.constants import (
    RESET_PASSWORD_TOKEN_BYTES,
    RESET_PASSWORD_TOKEN_EXPIRATION_TIME,
    EmailSubjectsEnum,
    EmailTextEnum,
    RedisNamesEnum,
)
from app.api.v1.models import PaginationModel, SearchModel, SortingModel
from app.api.v1.models.user import (
    CreateUserRequestModel,
    UpdateUserRequestModel,
    User,
    UsersFilterModel,
)
from app.api.v1.repositories.user import UserRepository
from app.api.v1.services import BaseService
from app.constants import HTTPErrorMessagesEnum
from app.services.redis.service import RedisService
from app.tasks import SendEmailTask


class UserService(BaseService):
    """User service for encapsulating business logic."""

    def __init__(
        self,
        repository: UserRepository = Depends(),
        redis_service: RedisService = Depends(),
        send_email_task: SendEmailTask = Depends(),
    ) -> None:
        """Initializes the UserService.

        This method sets up the MongoDB service instance for data access.

        Args:
            repository (UserRepository): An instance of the User repository.
            redis_service (RedisService): Redis service.
            send_email_task (SendEmailTask): Send email task.

        """

        self.repository = repository

        self.redis_service = redis_service

        self.send_email_task = send_email_task

    async def get_items(
        self,
        filter_: UsersFilterModel,
        search: SearchModel,
        sorting: SortingModel,
        pagination: PaginationModel,
    ) -> List[Mapping[str, Any]]:
        """Retrieves a list of users based on parameters.

        Args:
            filter_ (UsersFilterModel): Parameters for list filtering.
            search (SearchModel): Parameters for list searching.
            sorting (SortingModel): Parameters for sorting.
            pagination (PaginationModel): Parameters for pagination.

        Returns:
            List[Mapping[str, Any]]: The retrieved list of users.

        """

        return await self.repository.get_items(
            search=search.search,
            sort_by=sorting.sort_by,
            sort_order=sorting.sort_order,
            page=pagination.page,
            page_size=pagination.page_size,
            roles=[role.name for role in filter_.roles],
            deleted=filter_.deleted,
        )

    async def count_documents(
        self, filter_: UsersFilterModel, search: SearchModel
    ) -> int:
        """Counts documents based on parameters.

        Args:
            filter_ (UsersFilterModel): Parameters for list filtering.
            search (SearchModel): Parameters for list searching.

        Returns:
            int: Count of documents.

        """

        return await self.repository.count_documents(
            search=search.search,
            roles=[role.name for role in filter_.roles],
            deleted=filter_.deleted,
        )

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
        """Updates a user by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the user.
            item (Any): Data to update user.

        Returns:
            User | None: The updated user.

        """

        await self.repository.update_item_by_id(
            id_=id_,
            item={
                **item.model_dump(exclude={"roles"}),
                "roles": [role.name for role in item.roles],
                "birthdate": arrow.get(item.birthdate).datetime,
                "updated_at": arrow.utcnow().datetime,
            },
        )

        return await self.get_item_by_id(id_=id_)

    async def update_item_password(self, id_: ObjectId, password: str) -> None:
        """Updates user password by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the user.
            password (str): Password to update.

        """

        password = Password.get_password_hash(password=password)

        await self.repository.update_item_by_id(
            id_=id_,
            item={
                "hashed_password": password,
                "updated_at": arrow.utcnow().datetime,
            },
        )

    async def delete_item_by_id(self, id_: ObjectId) -> None:
        """Softly deletes a user by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the user.

        """

        await self.repository.update_item_by_id(
            id_=id_, item={"deleted": True, "updated_at": arrow.utcnow().datetime}
        )

    async def request_reset_item_password(self, user: User) -> None:
        """Requests user's password reset.

        Args:
            user (User): User that requests password reset.

        """

        token = secrets.token_urlsafe(RESET_PASSWORD_TOKEN_BYTES)

        hashed_token = hashlib.sha256(token.encode()).hexdigest()

        self.redis_service.set(
            name=RedisNamesEnum.RESET_PASSWORD.value.format(user_id=user.id),
            value=hashed_token,
            ttl=RESET_PASSWORD_TOKEN_EXPIRATION_TIME,
        )

        await self.send_email_task(
            to_emails=user.email,
            subject=EmailSubjectsEnum.RESET_PASSWORD.value,
            plain_text_content=EmailTextEnum.RESET_PASSWORD.value.format(token=token),
        )

    async def reset_item_password(
        self, id_: ObjectId, token: str, password: str
    ) -> None:
        """Resets user password.

        Args:
            id_ (ObjectId): The unique identifier of the user.
            token (str): Verification token.
            password (str): Password to update.

        """

        hashed_token = hashlib.sha256(token.encode()).hexdigest()

        cached_token = self.redis_service.get(
            name=RedisNamesEnum.RESET_PASSWORD.value.format(user_id=id_)
        )

        if cached_token is None or cached_token != hashed_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=HTTPErrorMessagesEnum.INVALID_RESET_PASSWORD_TOKEN.value,
            )

        await self.update_item_password(id_=id_, password=password)

        self.redis_service.delete(
            name=RedisNamesEnum.RESET_PASSWORD.value.format(user_id=id_)
        )
