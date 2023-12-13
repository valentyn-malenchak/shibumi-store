"""Module that contains base entity abstract class."""

import abc

from app.services.mongo.mongo import MongoDBService


class BaseEntity(abc.ABC):
    """Base entity abstract class."""


class StoredEntity(BaseEntity):
    """Entity which data is stored in database."""

    def __init__(self) -> None:
        """Initialization method."""

        self._mongo = MongoDBService()
