"""Contains a migration that creates/drops roles_scopes role field unique index."""

from mongodb_migrations.base import BaseMigration


class Migration(BaseMigration):  # type: ignore
    """Migration that creates/drops roles_scopes role field unique index."""

    def upgrade(self) -> None:
        """Creates a role index."""
        self.db["roles_scopes"].create_index("role", unique=True)

    def downgrade(self) -> None:
        """Drops a role index."""
        self.db["roles_scopes"].drop_index("role_1")
