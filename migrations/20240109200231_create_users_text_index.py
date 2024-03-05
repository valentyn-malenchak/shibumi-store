"""Contains a migration that creates/drops text index for users collection."""

from mongodb_migrations.base import BaseMigration

from app.services.mongo.constants import MongoCollectionsEnum


class Migration(BaseMigration):  # type: ignore
    """Migration that creates/drops text index for users collection."""

    def upgrade(self) -> None:
        """Creates a text index."""
        self.db[MongoCollectionsEnum.USERS].create_index(
            [
                ("first_name", "text"),
                ("last_name", "text"),
                ("patronymic_name", "text"),
                ("username", "text"),
                ("email", "text"),
                ("phone_number", "text"),
            ]
        )

    def downgrade(self) -> None:
        """Drops a text index."""
        self.db[MongoCollectionsEnum.USERS].drop_index(
            "first_name_text_last_name_text_patronymic_name_text_username_text_email_text_phone_number_text"
        )
