"""
Contains a migration that creates/drops parameters machine name field unique index.
"""

from mongodb_migrations.base import BaseMigration


class Migration(BaseMigration):  # type: ignore
    """Migration that creates/drops parameters machine name field unique index."""

    def upgrade(self) -> None:
        """Creates machine name index."""
        self.db["parameters"].create_index("machine_name", unique=True)

    def downgrade(self) -> None:
        """Drops machine name index."""
        self.db["parameters"].drop_index("machine_name_1")
