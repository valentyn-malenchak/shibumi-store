"""Module that contains user service class."""

from collections.abc import Mapping
from typing import Any

from bson import ObjectId
from fastapi import BackgroundTasks, Depends

from app.api.v1.auth.password import Password
from app.api.v1.constants import (
    EmailSubjectsEnum,
    EmailTextEnum,
    RedisNamesEnum,
    RedisNamesTTLEnum,
)
from app.api.v1.models import Pagination, Search, Sorting
from app.api.v1.models.cart import CartCreateData
from app.api.v1.models.user import (
    BaseUserCreateData,
    BaseUserUpdateData,
    User,
    UserCreateData,
    UserFilter,
    UserUpdateData,
)
from app.api.v1.repositories.cart import CartRepository
from app.api.v1.repositories.user import UserRepository
from app.api.v1.services import BaseService
from app.exceptions import InvalidVerificationTokenError
from app.services.mongo.transaction_manager import TransactionManager
from app.services.redis.service import RedisService
from app.services.send_grid.service import SendGridService
from app.utils.token import VerificationToken


class UserService(BaseService):
    """User service for encapsulating business logic."""

    def __init__(  # noqa: PLR0913
        self,
        background_tasks: BackgroundTasks,
        redis_service: RedisService = Depends(),
        transaction_manager: TransactionManager = Depends(),
        repository: UserRepository = Depends(),
        cart_repository: CartRepository = Depends(),
        send_grid_service: SendGridService = Depends(),
    ) -> None:
        """Initializes the UserService.

        Args:
            background_tasks (BackgroundTasks): Background tasks.
            redis_service (RedisService): Redis service.
            transaction_manager (TransactionManager): Transaction manager.
            repository (UserRepository): An instance of the User repository.
            cart_repository (CartRepository): An instance of the cart repository.
            send_grid_service (SendGridService): SendGrid service.

        """

        super().__init__(
            background_tasks=background_tasks,
            redis_service=redis_service,
            transaction_manager=transaction_manager,
        )

        self.repository = repository

        self.cart_repository = cart_repository

        self.send_grid_service = send_grid_service

    async def get(
        self,
        filter_: UserFilter,
        search: Search,
        sorting: Sorting,
        pagination: Pagination,
    ) -> list[Mapping[str, Any]]:
        """Retrieves a list of users based on parameters.

        Args:
            filter_ (UserFilter): Parameters for list filtering.
            search (Search): Parameters for list searching.
            sorting (Sorting): Parameters for sorting.
            pagination (Pagination): Parameters for pagination.

        Returns:
            list[Mapping[str, Any]]: The retrieved list of users.

        """
        return await self.repository.get(
            filter_=filter_,
            search=search,
            sorting=sorting,
            pagination=pagination,
        )

    async def count(self, filter_: UserFilter, search: Search) -> int:
        """Counts users based on parameters.

        Args:
            filter_ (UserFilter): Parameters for list filtering.
            search (Search): Parameters for list searching.

        Returns:
            int: Count of users.

        """
        return await self.repository.count(
            filter_=filter_,
            search=search,
        )

    async def get_by_id(self, id_: ObjectId) -> User:
        """Retrieves a user by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the item.

        Returns:
            User: User object.

        """
        return await self.repository.get_by_id(id_=id_)

    async def create(self, data: BaseUserCreateData) -> User:
        """Creates a new user.

        Args:
            data (BaseUserCreateData): The data for the new user.

        Returns:
            User: Created user.

        """

        password = Password.get_password_hash(password=data.password)

        id_ = await self.repository.create(
            data=UserCreateData(**data.model_dump(), hashed_password=password)
        )

        # Initialize user's cart
        await self.cart_repository.create(data=CartCreateData(user_id=id_))

        user = await self.get_by_id(id_=id_)

        await self.request_verify_email(item=user)

        return user

    async def update(self, item: User, data: BaseUserUpdateData) -> User:
        """Updates a user object.

        Args:
            item (User): User object.
            data (BaseUserUpdateData): Data to update user.

        Returns:
            User: The updated user.

        """

        emails_match = item.email == data.email

        user = await self.repository.get_and_update_by_id(
            id_=item.id,
            data=UserUpdateData(
                **data.model_dump(), email_verified=emails_match and item.email_verified
            ),
        )

        if emails_match is False:
            await self.request_verify_email(item=user)

        return user

    async def update_by_id(self, id_: Any, data: Any) -> Any:
        """Updates a user by its unique identifier.

        Args:
            id_ (Any): The unique identifier of the user.
            data (Any): Data to update user.

        Returns:
            Any: The updated user.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def update_password(self, id_: ObjectId, password: str) -> None:
        """Updates user's password by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the user.
            password (str): Password to update.

        """

        password = Password.get_password_hash(password=password)

        await self.repository.update_password(id_=id_, hashed_password=password)

    async def delete_by_id(self, id_: ObjectId) -> None:
        """Softly deletes a user by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the user.

        """

        await self.repository.delete_by_id(id_=id_)

    async def delete(self, item: Any) -> None:
        """Deletes a user.

        Args:
            item (Any): User object.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def get_by_username(self, username: str) -> User:
        """Retrieves a user by its username.

        Args:
            username (str): Username.

        Returns:
            User: User object.

        """
        return await self.repository.get_by_username(username=username)

    async def request_reset_password(self, item: User) -> None:
        """Requests user's password reset.

        Args:
            item (User): User that requests password reset.

        """

        token = VerificationToken.generate()

        self.redis_service.set(
            name=RedisNamesEnum.RESET_PASSWORD.format(user_id=item.id),
            value=token.hash(),
            ttl=RedisNamesTTLEnum.RESET_PASSWORD.value,
        )

        self.background_tasks.add_task(
            self.send_grid_service.send,
            to_emails=item.email,
            subject=EmailSubjectsEnum.RESET_PASSWORD,
            plain_text_content=EmailTextEnum.RESET_PASSWORD.format(token=token.value),
        )

    async def reset_password(self, id_: ObjectId, token: str, password: str) -> None:
        """Resets user's password.

        Args:
            id_ (ObjectId): The unique identifier of the user.
            token (str): Verification token.
            password (str): Password to update.

        Raises:
            InvalidVerificationTokenError: in case verification token is invalid.

        """

        hashed_token = VerificationToken(token).hash()

        cached_token = self.redis_service.get(
            name=RedisNamesEnum.RESET_PASSWORD.format(user_id=id_)
        )

        if cached_token is None or cached_token != hashed_token:
            raise InvalidVerificationTokenError

        await self.update_password(id_=id_, password=password)

        self.redis_service.delete(
            name=RedisNamesEnum.RESET_PASSWORD.format(user_id=id_)
        )

    async def request_verify_email(self, item: User) -> None:
        """Requests user's email verification.

        Args:
            item (User): User that requests email verification.

        """

        token = VerificationToken.generate()

        self.redis_service.set(
            name=RedisNamesEnum.EMAIL_VERIFICATION.format(user_id=item.id),
            value=token.hash(),
            ttl=RedisNamesTTLEnum.EMAIL_VERIFICATION.value,
        )

        self.background_tasks.add_task(
            self.send_grid_service.send,
            to_emails=item.email,
            subject=EmailSubjectsEnum.EMAIL_VERIFICATION,
            plain_text_content=EmailTextEnum.EMAIL_VERIFICATION.format(
                token=token.value
            ),
        )

    async def verify_email(self, id_: ObjectId, token: str) -> None:
        """Verifies user's email.

        Args:
            id_ (ObjectId): The unique identifier of the user.
            token (str): Verification token.

        Raises:
            InvalidVerificationTokenError: in case verification token is invalid.

        """

        hashed_token = VerificationToken(token).hash()

        cached_token = self.redis_service.get(
            name=RedisNamesEnum.EMAIL_VERIFICATION.format(user_id=id_)
        )

        if cached_token is None or cached_token != hashed_token:
            raise InvalidVerificationTokenError

        await self.repository.verify_email(id_=id_)

        self.redis_service.delete(
            name=RedisNamesEnum.EMAIL_VERIFICATION.format(user_id=id_)
        )
