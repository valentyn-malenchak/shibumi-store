"""Contains a migration that creates/drops text index for products collection."""

from mongodb_migrations.base import BaseMigration


class Migration(BaseMigration):  # type: ignore
    """Migration that creates/drops text index for products collection."""

    def upgrade(self) -> None:
        """Creates a text index."""
        self.db["products"].create_index(
            [
                ("name", "text"),
                ("synopsis", "text"),
                ("description", "text"),
            ]
        )

    def downgrade(self) -> None:
        """Drops a text index."""
        self.db["products"].drop_index("name_text_synopsis_text_description_text")
