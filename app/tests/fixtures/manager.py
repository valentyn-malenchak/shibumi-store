"""Contains fixture loader class."""

import os
from typing import Any, ClassVar

from injector import Injector

from app.api.v1.repositories import BaseRepository
from app.api.v1.repositories.cart import CartRepository
from app.api.v1.repositories.category_parameters import (
    CategoryParametersRepository,
)
from app.api.v1.repositories.comment import CommentRepository
from app.api.v1.repositories.product import ProductRepository
from app.api.v1.repositories.thread import ThreadRepository
from app.api.v1.repositories.user import UserRepository
from app.api.v1.repositories.vote import VoteRepository
from app.loaders import JSONFileLoader
from app.services.mongo.constants import MongoCollectionsEnum
from app.services.mongo.transaction_manager import TransactionManager


class FileFixtureManager:
    """File fixture manager."""

    _injector = Injector()

    # contains collection mapping to its repository
    _fixture_repositories: ClassVar[dict[MongoCollectionsEnum, BaseRepository]] = {
        MongoCollectionsEnum.USERS: _injector.get(UserRepository),
        MongoCollectionsEnum.PRODUCTS: _injector.get(ProductRepository),
        MongoCollectionsEnum.CATEGORY_PARAMETERS: _injector.get(
            CategoryParametersRepository
        ),
        MongoCollectionsEnum.CARTS: _injector.get(CartRepository),
        MongoCollectionsEnum.THREADS: _injector.get(ThreadRepository),
        MongoCollectionsEnum.COMMENTS: _injector.get(CommentRepository),
        MongoCollectionsEnum.VOTES: _injector.get(VoteRepository),
    }

    def __init__(
        self, collection_names: list[MongoCollectionsEnum] | None = None
    ) -> None:
        """File fixture manager initialization method.

        Args:
            collection_names (list[MongoCollectionsEnum] | None): List of
            collections to be handled. Defaults to None.

        """

        self.transaction_manager = self._injector.get(TransactionManager)

        self.collection_names = (
            collection_names
            if collection_names is not None
            else list(self._fixture_repositories.keys())
        )

    @staticmethod
    def _load_fixture(fixture_file_path: str) -> Any:
        """Loads data from fixture file.

        Args:
            fixture_file_path (str): Fixture file path.

        Returns:
            Any: Fixture content.

        """
        return JSONFileLoader(file_path=fixture_file_path).load()

    async def load(self) -> None:
        """Loads data from fixtures into collections."""

        async with self.transaction_manager as session:
            for collection in self.collection_names:
                fixture_file_path = os.path.join(
                    "app", "tests", "fixtures", "json", f"{collection}.json"
                )

                data = self._load_fixture(fixture_file_path)

                repository = self._fixture_repositories[collection]

                await repository.create_many(documents=data, session=session)

    async def clear(self) -> None:
        """Clear collections from loaded data."""

        async with self.transaction_manager as session:
            # clean all collections which have fixtures
            for collection in list(self._fixture_repositories.keys()):
                repository = self._fixture_repositories[collection]

                await repository.delete_all(session=session)
