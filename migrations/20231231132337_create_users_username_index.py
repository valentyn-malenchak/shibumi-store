"""Contains a migration that creates/drops users username field unique index."""

from mongodb_migrations.base import BaseMigration

from app.services.mongo.constants import MongoCollectionsEnum


class Migration(BaseMigration):  # type: ignore
    """Migration that creates/drops users username field unique index."""

    def upgrade(self) -> None:
        """Creates a username index."""
        self.db[MongoCollectionsEnum.USERS].create_index("username", unique=True)

    def downgrade(self) -> None:
        """Drops a username index."""
        self.db[MongoCollectionsEnum.USERS].drop_index("username_1")
