"""Contains a migration that creates/drops cart user_id field unique index."""

from mongodb_migrations.base import BaseMigration

from app.services.mongo.constants import MongoCollectionsEnum


class Migration(BaseMigration):  # type: ignore
    """Migration that creates/drops cart user_id field unique index."""

    def upgrade(self) -> None:
        """Creates a user_id index."""
        self.db[MongoCollectionsEnum.CART].create_index("user_id", unique=True)

    def downgrade(self) -> None:
        """Drops a user_id index."""
        self.db[MongoCollectionsEnum.CART].drop_index("user_id_1")
