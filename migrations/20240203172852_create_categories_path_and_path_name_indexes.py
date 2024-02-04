"""
Contains a migration that creates/drops categories path and path name
fields unique indexes.
"""

from mongodb_migrations.base import BaseMigration


class Migration(BaseMigration):  # type: ignore
    """
    Migration that creates/drops categories path and path name
    fields unique indexes.
    """

    def upgrade(self) -> None:
        """Creates path and path name indexes."""
        # used as "Materialized Path" pattern
        self.db["categories"].create_index("path", unique=True)
        self.db["categories"].create_index("path_name", unique=True)

    def downgrade(self) -> None:
        """Drops path and path name indexes."""
        self.db["categories"].drop_index("path_name_1")
        self.db["categories"].drop_index("path_1")
