"""Contains a migration that creates/drops roles role field unique index."""

from mongodb_migrations.base import BaseMigration

from app.services.mongo.constants import MongoCollectionsEnum


class Migration(BaseMigration):  # type: ignore
    """Migration that creates/drops roles role field unique index."""

    def upgrade(self) -> None:
        """Creates a role index."""
        self.db[MongoCollectionsEnum.ROLES].create_index("role", unique=True)

    def downgrade(self) -> None:
        """Drops a role index."""
        self.db[MongoCollectionsEnum.ROLES].drop_index("role_1")
