"""Contains a migration that creates/drops roles machine_name field unique index."""

from mongodb_migrations.base import BaseMigration

from app.services.mongo.constants import MongoCollectionsEnum


class Migration(BaseMigration):  # type: ignore
    """Migration that creates/drops roles machine_name field unique index."""

    def upgrade(self) -> None:
        """Creates a machine_name index."""
        self.db[MongoCollectionsEnum.ROLES].create_index("machine_name", unique=True)

    def downgrade(self) -> None:
        """Drops a machine_name index."""
        self.db[MongoCollectionsEnum.ROLES].drop_index("machine_name_1")
