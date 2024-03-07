"""
Contains a migration that creates/drops categories path and machine_name
fields unique indexes.
"""

from mongodb_migrations.base import BaseMigration

from app.services.mongo.constants import MongoCollectionsEnum


class Migration(BaseMigration):  # type: ignore
    """
    Migration that creates/drops categories path and machine_name
    fields unique indexes.
    """

    def upgrade(self) -> None:
        """Creates path and machine_name indexes."""
        # used as "Materialized Path" pattern
        self.db[MongoCollectionsEnum.CATEGORIES].create_index("path", unique=True)
        self.db[MongoCollectionsEnum.CATEGORIES].create_index(
            "machine_name", unique=True
        )

    def downgrade(self) -> None:
        """Drops path and machine_name indexes."""
        self.db[MongoCollectionsEnum.CATEGORIES].drop_index("machine_name_1")
        self.db[MongoCollectionsEnum.CATEGORIES].drop_index("path_1")
