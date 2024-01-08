"""Contains a migration that inserts/deletes role scopes."""

from mongodb_migrations.base import BaseMigration

from app.api.v1.constants import RolesEnum, ScopesEnum


class Migration(BaseMigration):  # type: ignore
    """Migration that inserts/deletes role scopes."""

    def upgrade(self) -> None:
        """Inserts roles scopes."""
        self.db["roles_scopes"].insert_many(
            [
                {
                    "role": RolesEnum.CUSTOMER.name,
                    "scopes": [
                        ScopesEnum.AUTH_REFRESH_TOKEN.name,
                        ScopesEnum.USERS_GET_ME.name,
                        ScopesEnum.USERS_UPDATE_USER.name,
                        ScopesEnum.USERS_DELETE_USER.name,
                    ],
                },
                {
                    "role": RolesEnum.SUPPORT.name,
                    "scopes": [
                        ScopesEnum.AUTH_REFRESH_TOKEN.name,
                        ScopesEnum.USERS_GET_ME.name,
                        ScopesEnum.USERS_GET_USER.name,
                        ScopesEnum.USERS_CREATE_USER.name,
                        ScopesEnum.USERS_UPDATE_USER.name,
                        ScopesEnum.USERS_DELETE_USER.name,
                    ],
                },
                {
                    "role": RolesEnum.WAREHOUSE_STUFF.name,
                    "scopes": [
                        ScopesEnum.AUTH_REFRESH_TOKEN.name,
                        ScopesEnum.USERS_GET_ME.name,
                    ],
                },
                {
                    "role": RolesEnum.CONTENT_MANAGER.name,
                    "scopes": [
                        ScopesEnum.AUTH_REFRESH_TOKEN.name,
                        ScopesEnum.USERS_GET_ME.name,
                    ],
                },
                {
                    "role": RolesEnum.MARKETING_MANAGER.name,
                    "scopes": [
                        ScopesEnum.AUTH_REFRESH_TOKEN.name,
                        ScopesEnum.USERS_GET_ME.name,
                    ],
                },
                {
                    "role": RolesEnum.ADMIN.name,
                    "scopes": [
                        ScopesEnum.AUTH_REFRESH_TOKEN.name,
                        ScopesEnum.HEALTH_GET_HEALTH.name,
                        ScopesEnum.USERS_GET_ME.name,
                        ScopesEnum.USERS_GET_USER.name,
                        ScopesEnum.USERS_CREATE_USER.name,
                        ScopesEnum.USERS_UPDATE_USER.name,
                        ScopesEnum.USERS_DELETE_USER.name,
                    ],
                },
            ]
        )

    def downgrade(self) -> None:
        """Drops roles scopes."""
        self.db["roles_scopes"].delete_many(filter={})
