"""
Contains a migration that creates/drops votes comment_id/user_id
fields unique index.
"""

from mongodb_migrations.base import BaseMigration

from app.services.mongo.constants import MongoCollectionsEnum, SortingValuesEnum


class Migration(BaseMigration):  # type: ignore
    """Migration that creates/drops votes comment_id/user_id fields unique index."""

    def upgrade(self) -> None:
        """Creates a comment_id/user_id index."""
        self.db[MongoCollectionsEnum.VOTES].create_index(
            {"comment_id": SortingValuesEnum.ASC, "user_id": SortingValuesEnum.ASC},
            unique=True,
        )

    def downgrade(self) -> None:
        """Drops a comment_id/user_id index."""
        self.db[MongoCollectionsEnum.VOTES].drop_index("comment_id_1_user_id_1")
