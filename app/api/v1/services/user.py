"""Module that contains user service class."""


from typing import Any, List, Mapping

import arrow
from bson import ObjectId
from fastapi import BackgroundTasks, Depends, HTTPException, status
from pymongo.errors import DuplicateKeyError

from app.api.v1.auth.password import Password
from app.api.v1.constants import (
    EmailSubjectsEnum,
    EmailTextEnum,
    RedisNamesEnum,
    RedisNamesTTLEnum,
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
from app.services.mongo.transaction_manager import TransactionManager
from app.services.redis.service import RedisService
from app.services.send_grid.service import SendGridService
from app.utils.token import VerificationToken


class UserService(BaseService):
    """User service for encapsulating business logic."""

    def __init__(  # noqa: PLR0913
        self,
        background_tasks: BackgroundTasks,
        repository: UserRepository = Depends(),
        redis_service: RedisService = Depends(),
        transaction_manager: TransactionManager = Depends(),
        send_grid_service: SendGridService = Depends(),
    ) -> None:
        """Initializes the UserService.

        Args:
            background_tasks (BackgroundTasks): Background tasks.
            repository (UserRepository): An instance of the User repository.
            redis_service (RedisService): Redis service.
            transaction_manager (TransactionManager): Transaction manager.
            send_grid_service (SendGridService): SendGrid service.

        """

        super().__init__(
            background_tasks=background_tasks,
            redis_service=redis_service,
            transaction_manager=transaction_manager,
        )

        self.repository = repository

        self.send_grid_service = send_grid_service

    async def get(
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

        return await self.repository.get(
            search=search.search,
            sort_by=sorting.sort_by,
            sort_order=sorting.sort_order,
            page=pagination.page,
            page_size=pagination.page_size,
            roles=[role.name for role in filter_.roles],
            deleted=filter_.deleted,
        )

    async def count(self, filter_: UsersFilterModel, search: SearchModel) -> int:
        """Counts documents based on parameters.

        Args:
            filter_ (UsersFilterModel): Parameters for list filtering.
            search (SearchModel): Parameters for list searching.

        Returns:
            int: Count of documents.

        """

        return await self.repository.count(
            search=search.search,
            roles=[role.name for role in filter_.roles],
            deleted=filter_.deleted,
        )

    async def get_by_id(self, id_: ObjectId) -> User | None:
        """Retrieves an item by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the item.

        Returns:
            User | None: User object or None.

        """

        user = await self.repository.get_by_id(id_=id_)

        return User(**user) if user is not None else None

    async def get_by_username(self, username: str) -> User | None:
        """Retrieves an item by its username.

        Args:
            username (str): Username.

        Returns:
            User | None: User object or None.

        """

        user = await self.repository.get_by_username(username=username)

        return User(**user) if user is not None else None

    async def create(self, item: CreateUserRequestModel) -> User | None:
        """Creates a new user.

        Args:
            item (CreateUserRequestModel): The data for the new user.

        Returns:
            User | None: The created user.

        """

        password = Password.get_password_hash(password=item.password)

        try:
            id_ = await self.repository.create(
                item={
                    # Replaces plain password on hashed one
                    **item.model_dump(exclude={"password", "roles"}),
                    "email_verified": False,
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

        user = await self.get_by_id(id_=id_)

        await self.request_verify_email(user=user)  # type: ignore

        return user

    async def update_by_id(
        self, id_: ObjectId, item: UpdateUserRequestModel
    ) -> User | None:
        """Updates a user by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the user.
            item (Any): Data to update user.

        Returns:
            User | None: The updated user.

        """

        await self.repository.update_by_id(
            id_=id_,
            item={
                **item.model_dump(exclude={"roles"}),
                "roles": [role.name for role in item.roles],
                "birthdate": arrow.get(item.birthdate).datetime,
                "updated_at": arrow.utcnow().datetime,
            },
        )

        return await self.get_by_id(id_=id_)

    async def update_password(self, id_: ObjectId, password: str) -> None:
        """Updates user's password by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the user.
            password (str): Password to update.

        """

        password = Password.get_password_hash(password=password)

        await self.repository.update_by_id(
            id_=id_,
            item={
                "hashed_password": password,
                "updated_at": arrow.utcnow().datetime,
            },
        )

    async def _update_email_verified(self, id_: ObjectId) -> None:
        """Updates user's email verification flag.

        Args:
            id_ (ObjectId): The unique identifier of the user.

        """

        await self.repository.update_by_id(
            id_=id_,
            item={
                "email_verified": True,
                "updated_at": arrow.utcnow().datetime,
            },
        )

    async def delete_by_id(self, id_: ObjectId) -> None:
        """Softly deletes a user by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the user.

        """

        await self.repository.update_by_id(
            id_=id_, item={"deleted": True, "updated_at": arrow.utcnow().datetime}
        )

    async def request_reset_password(self, user: User) -> None:
        """Requests user's password reset.

        Args:
            user (User): User that requests password reset.

        """

        token = VerificationToken.generate()

        self.redis_service.set(
            name=RedisNamesEnum.RESET_PASSWORD.value.format(user_id=user.id),
            value=token.hash(),
            ttl=RedisNamesTTLEnum.RESET_PASSWORD.value,
        )

        self.background_tasks.add_task(
            self.send_grid_service.send,
            to_emails=user.email,
            subject=EmailSubjectsEnum.RESET_PASSWORD.value,
            plain_text_content=EmailTextEnum.RESET_PASSWORD.value.format(
                token=token.value
            ),
        )

    async def reset_password(self, id_: ObjectId, token: str, password: str) -> None:
        """Resets user's password.

        Args:
            id_ (ObjectId): The unique identifier of the user.
            token (str): Verification token.
            password (str): Password to update.

        """

        hashed_token = VerificationToken(token).hash()

        cached_token = self.redis_service.get(
            name=RedisNamesEnum.RESET_PASSWORD.value.format(user_id=id_)
        )

        if cached_token is None or cached_token != hashed_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=HTTPErrorMessagesEnum.INVALID_RESET_PASSWORD_TOKEN.value,
            )

        await self.update_password(id_=id_, password=password)

        self.redis_service.delete(
            name=RedisNamesEnum.RESET_PASSWORD.value.format(user_id=id_)
        )

    async def request_verify_email(self, user: User) -> None:
        """Requests user's email verification.

        Args:
            user (User): User that requests email verification.

        """

        token = VerificationToken.generate()

        self.redis_service.set(
            name=RedisNamesEnum.EMAIL_VERIFICATION.value.format(user_id=user.id),
            value=token.hash(),
            ttl=RedisNamesTTLEnum.EMAIL_VERIFICATION.value,
        )

        self.background_tasks.add_task(
            self.send_grid_service.send,
            to_emails=user.email,
            subject=EmailSubjectsEnum.EMAIL_VERIFICATION.value,
            plain_text_content=EmailTextEnum.EMAIL_VERIFICATION.value.format(
                token=token.value
            ),
        )

    async def verify_email(self, id_: ObjectId, token: str) -> None:
        """Verifies user's email.

        Args:
            id_ (ObjectId): The unique identifier of the user.
            token (str): Verification token.

        """

        hashed_token = VerificationToken(token).hash()

        cached_token = self.redis_service.get(
            name=RedisNamesEnum.EMAIL_VERIFICATION.value.format(user_id=id_)
        )

        if cached_token is None or cached_token != hashed_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=HTTPErrorMessagesEnum.INVALID_EMAIL_VERIFICATION_TOKEN.value,
            )

        await self._update_email_verified(id_=id_)

        self.redis_service.delete(
            name=RedisNamesEnum.EMAIL_VERIFICATION.value.format(user_id=id_)
        )
