"""Module that contains cart service class."""

from typing import Any

import arrow
from bson import ObjectId
from fastapi import BackgroundTasks, Depends

from app.api.v1.models.cart import Cart, CartProduct
from app.api.v1.repositories.cart import CartRepository
from app.api.v1.services import BaseService
from app.exceptions import EntityIsNotFoundError
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

    async def get(self, *_: Any) -> Any:
        """Retrieves a list of carts based on parameters.

        Args:
            _ (Any): Parameters for list filtering, searching, sorting and pagination.

        Returns:
            list[Mapping[str, Any]]: The retrieved list of carts.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def count(self, *_: Any) -> int:
        """Counts documents based on parameters.

        Args:
            _ (Any): Parameters for list filtering and searching.

        Returns:
            int: Count of documents.

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

        Raises:
            EntityIsNotFoundError: In case cart is not found.

        """

        cart = await self.repository.get_by_id(id_=id_)

        if cart is None:
            raise EntityIsNotFoundError

        return Cart(**cart)

    async def get_by_user_id(self, user_id: ObjectId) -> Cart:
        """Retrieves a cart by user unique identifier.

        Args:
            user_id (ObjectId): The unique identifier of the user.

        Returns:
            Cart: The retrieved cart.

        Raises:
            EntityIsNotFoundError: In case cart is not found.

        """

        cart = await self.repository.get_by_user_id(user_id=user_id)

        if cart is None:
            raise EntityIsNotFoundError

        return Cart(**cart)

    async def create(self, user_id: ObjectId) -> Cart:
        """Creates a new cart.

        Args:
            user_id (Any): User unique identifier.

        Returns:
            Cart: Created cart.

        """

        id_ = await self.repository.create(
            data={
                "user_id": user_id,
                "products": [],
                "created_at": arrow.utcnow().datetime,
                "updated_at": None,
            }
        )

        return await self.get_by_id(id_=id_)

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

    async def update_by_id(self, id_: ObjectId, products: list[CartProduct]) -> Cart:
        """Updates a cart by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the cart.
            products (list[CartProduct]): List of products for cart update.

        Returns:
            Cart: The updated cart.

        """

        await self.repository.update_by_id(
            id_=id_,
            data={
                "products": [product.model_dump() for product in products],
                "updated_at": arrow.utcnow().datetime,
            },
        )

        return await self.get_by_id(id_=id_)

    async def delete_by_id(self, id_: ObjectId) -> None:
        """Deletes a cart by its unique identifier.

        Args:
            id_ (ObjectId): The unique identifier of the cart.

        Raises:
            NotImplementedError: This method is not implemented.

        """
        raise NotImplementedError

    async def add_product_to_the_cart(self, item: Cart, product: CartProduct) -> Cart:
        """Adds new product to the cart.

        Args:
            item (Cart): Cart object.
            product (CartProduct): Product to be added.

        Returns:
            Cart: Updated cart.

        """

        return await self.update_by_id(id_=item.id, products=[*item.products, product])

    async def update_product_to_the_cart(
        self, item: Cart, product: CartProduct
    ) -> Cart:
        """Updates new product to the cart.

        Args:
            item (Cart): Cart object.
            product (CartProduct): Product to be updated.

        Returns:
            Cart: Updated cart.

        """

        return await self.update_by_id(
            id_=item.id,
            products=[
                # Replaces product object if ids match
                cart_product if cart_product.id != product.id else product
                for cart_product in item.products
            ],
        )
