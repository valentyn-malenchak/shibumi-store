"""Contains a migration that creates/drops products category_id field index."""

from mongodb_migrations.base import BaseMigration

from app.services.mongo.constants import MongoCollectionsEnum


class Migration(BaseMigration):  # type: ignore
    """Migration that creates/drops products category_id field index."""

    def upgrade(self) -> None:
        """Creates a category_id index."""
        self.db[MongoCollectionsEnum.PRODUCTS.value].create_index("category_id")

    def downgrade(self) -> None:
        """Drops a category_id index."""
        self.db[MongoCollectionsEnum.PRODUCTS.value].drop_index("category_id_1")
