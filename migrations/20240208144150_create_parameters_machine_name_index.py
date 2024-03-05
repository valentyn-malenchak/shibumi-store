"""
Contains a migration that creates/drops parameters machine name field unique index.
"""

from mongodb_migrations.base import BaseMigration

from app.services.mongo.constants import MongoCollectionsEnum


class Migration(BaseMigration):  # type: ignore
    """Migration that creates/drops parameters machine name field unique index."""

    def upgrade(self) -> None:
        """Creates machine name index."""
        self.db[MongoCollectionsEnum.PARAMETERS].create_index(
            "machine_name", unique=True
        )

    def downgrade(self) -> None:
        """Drops machine name index."""
        self.db[MongoCollectionsEnum.PARAMETERS].drop_index("machine_name_1")
