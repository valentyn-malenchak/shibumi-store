"""Module that contains cart service class."""

from typing import Any

from bson import ObjectId
from fastapi import BackgroundTasks, Depends

from app.api.v1.models import Pagination, Search, Sorting
from app.api.v1.models.cart import (
    Cart,
    CartProduct,
    CartProductQuantity,
)
from app.api.v1.repositories.cart import CartRepository
from app.api.v1.services import BaseService
from app.services.mongo.transaction_manager import TransactionManager
from app.services.redis.service import RedisService


class CartService(BaseService):
    """Cart service for encapsulating business logic."""

    def __init__(
        self,
        background_tasks: BackgroundTasks,
        redis_service: RedisService = Depends(),
        transaction_manager: TransactionManager = Depends(),
        repository: CartRepository = Depends(),
    ) -> None:
        """Initializes the cart service.

        Args:
            background_tasks (BackgroundTasks): Background tasks.
            redis_service (RedisService): Redis service.
            transaction_manager (TransactionManager): Transaction manager.
            repository (CartRepository): An instance of the Cart repository.

        """

        super().__init__(
            background_tasks=background_tasks,
            redis_service=redis_service,
            transaction_manager=transaction_manager,
        )

        self.repository = repository

    async def get(
        self, filter_: Any, search: Search, sorting: Sorting, pagination: Pagination
    ) -> Any:
        """Retrieves a list of carts based on parameters.

        Args:
            filter_ (Any): Parameters for list filtering.
            search (Search): Parameters for list searching.
            sorting (Sorting): Parameters for sorting.
            pagination (Pagination): Parameters for pagination.

        Returns:
            list[Mapping[str, Any]]: The retrieved list of carts.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def count(self, filter_: Any, search: Search) -> int:
        """Counts carts based on parameters.

        Args:
            filter_ (Any): Parameters for list filtering.
            search (Search): Parameters for list searching.

        Returns:
            int: Count of carts.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def get_by_id(self, id_: ObjectId) -> Cart:
        """Retrieves a cart by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the cart.

        Returns:
            Cart: The retrieved cart.

        """
        return await self.repository.get_by_id(id_=id_)

    async def get_by_user_id(self, user_id: ObjectId) -> Cart:
        """Retrieves a cart by user unique identifier.

        Args:
            user_id (ObjectId): BSON object identifier of requested user.

        Returns:
            Cart: The retrieved cart.

        """
        return await self.repository.get_by_user_id(user_id=user_id)

    async def create(self, data: Any) -> Any:
        """Creates a new cart.

        Args:
            data (Any): The data for the new cart.

        Returns:
            Any: Created cart.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def update(self, item: Any, data: Any) -> Any:
        """Updates a cart object.

        Args:
            item (Any): Cart object.
            data (Any): Data to update cart.

        Returns:
            Any: The updated cart.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def update_by_id(self, id_: ObjectId, data: Any) -> Any:
        """Updates a cart by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the cart.
            data (Any): Data to update cart.

        Returns:
            Any: The updated cart.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def delete_by_id(self, id_: ObjectId) -> None:
        """Deletes a cart by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the cart.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def delete(self, item: Any) -> None:
        """Deletes a cart.

        Args:
            item (Any): Cart object.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def add_product(self, id_: ObjectId, data: CartProduct) -> Cart:
        """Adds new product to the cart.

        Args:
            id_ (ObjectId): BSON object identifier of requested cart.
            data (CartProduct): Cart product data.

        Returns:
            Cart: Updated cart.

        """

        cart = await self.repository.add_product(
            id_=id_,
            product_id=data.id,
            quantity=data.quantity,
        )

        return Cart(**cart)

    async def update_product(
        self,
        id_: ObjectId,
        product_id: ObjectId,
        data: CartProductQuantity,
    ) -> Cart:
        """Updates product in the cart.

        Args:
            id_ (ObjectId): BSON object identifier of requested cart.
            product_id (ObjectId): The unique identifier of the product.
            data (CartProductQuantity): Cart product quantity.

        Returns:
            Cart: Updated cart.

        """

        cart = await self.repository.update_product(
            id_=id_,
            product_id=product_id,
            quantity=data.quantity,
        )

        return Cart(**cart)

    async def delete_product(self, id_: ObjectId, product_id: ObjectId) -> Cart:
        """Deletes product from the cart.

        Args:
            id_ (ObjectId): BSON object identifier of requested cart.
            product_id (ObjectId): The unique identifier of the product.

        Returns:
            Cart: Updated cart.

        """

        cart = await self.repository.delete_product(id_=id_, product_id=product_id)

        return Cart(**cart)
