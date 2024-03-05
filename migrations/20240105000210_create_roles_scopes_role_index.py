"""Contains a migration that creates/drops roles_scopes role field unique index."""

from mongodb_migrations.base import BaseMigration

from app.services.mongo.constants import MongoCollectionsEnum


class Migration(BaseMigration):  # type: ignore
    """Migration that creates/drops roles_scopes role field unique index."""

    def upgrade(self) -> None:
        """Creates a role index."""
        self.db[MongoCollectionsEnum.ROLES_SCOPES].create_index("role", unique=True)

    def downgrade(self) -> None:
        """Drops a role index."""
        self.db[MongoCollectionsEnum.ROLES_SCOPES].drop_index("role_1")
