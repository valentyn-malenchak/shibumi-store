"""Contains a migration that inserts/deletes role scopes."""

import arrow
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
                        ScopesEnum.USERS_UPDATE_USER_PASSWORD.name,
                        ScopesEnum.USERS_DELETE_USER.name,
                        ScopesEnum.CATEGORIES_GET_CATEGORIES.name,
                        ScopesEnum.CATEGORIES_GET_CATEGORY.name,
                        ScopesEnum.PRODUCTS_GET_PRODUCT.name,
                    ],
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "role": RolesEnum.SUPPORT.name,
                    "scopes": [
                        ScopesEnum.AUTH_REFRESH_TOKEN.name,
                        ScopesEnum.USERS_GET_ME.name,
                        ScopesEnum.USERS_GET_USERS.name,
                        ScopesEnum.USERS_GET_USER.name,
                        ScopesEnum.USERS_CREATE_USER.name,
                        ScopesEnum.USERS_UPDATE_USER.name,
                        ScopesEnum.USERS_UPDATE_USER_PASSWORD.name,
                        ScopesEnum.USERS_DELETE_USER.name,
                        ScopesEnum.CATEGORIES_GET_CATEGORIES.name,
                        ScopesEnum.CATEGORIES_GET_CATEGORY.name,
                        ScopesEnum.PRODUCTS_GET_PRODUCT.name,
                    ],
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "role": RolesEnum.WAREHOUSE_STUFF.name,
                    "scopes": [
                        ScopesEnum.AUTH_REFRESH_TOKEN.name,
                        ScopesEnum.USERS_GET_ME.name,
                        ScopesEnum.USERS_UPDATE_USER_PASSWORD.name,
                        ScopesEnum.CATEGORIES_GET_CATEGORIES.name,
                        ScopesEnum.CATEGORIES_GET_CATEGORY.name,
                        ScopesEnum.PRODUCTS_CREATE_PRODUCT.name,
                        ScopesEnum.PRODUCTS_GET_PRODUCT.name,
                    ],
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "role": RolesEnum.CONTENT_MANAGER.name,
                    "scopes": [
                        ScopesEnum.AUTH_REFRESH_TOKEN.name,
                        ScopesEnum.USERS_GET_ME.name,
                        ScopesEnum.USERS_UPDATE_USER_PASSWORD.name,
                        ScopesEnum.CATEGORIES_GET_CATEGORIES.name,
                        ScopesEnum.CATEGORIES_GET_CATEGORY.name,
                        ScopesEnum.PRODUCTS_GET_PRODUCT.name,
                    ],
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "role": RolesEnum.MARKETING_MANAGER.name,
                    "scopes": [
                        ScopesEnum.AUTH_REFRESH_TOKEN.name,
                        ScopesEnum.USERS_GET_ME.name,
                        ScopesEnum.USERS_UPDATE_USER_PASSWORD.name,
                        ScopesEnum.CATEGORIES_GET_CATEGORIES.name,
                        ScopesEnum.CATEGORIES_GET_CATEGORY.name,
                        ScopesEnum.PRODUCTS_GET_PRODUCT.name,
                    ],
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "role": RolesEnum.ADMIN.name,
                    "scopes": [
                        ScopesEnum.AUTH_REFRESH_TOKEN.name,
                        ScopesEnum.HEALTH_GET_HEALTH.name,
                        ScopesEnum.USERS_GET_ME.name,
                        ScopesEnum.USERS_GET_USERS.name,
                        ScopesEnum.USERS_GET_USER.name,
                        ScopesEnum.USERS_CREATE_USER.name,
                        ScopesEnum.USERS_UPDATE_USER.name,
                        ScopesEnum.USERS_UPDATE_USER_PASSWORD.name,
                        ScopesEnum.USERS_DELETE_USER.name,
                        ScopesEnum.CATEGORIES_GET_CATEGORIES.name,
                        ScopesEnum.CATEGORIES_GET_CATEGORY.name,
                        ScopesEnum.PRODUCTS_CREATE_PRODUCT.name,
                        ScopesEnum.PRODUCTS_GET_PRODUCT.name,
                    ],
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
            ]
        )

    def downgrade(self) -> None:
        """Drops roles scopes."""
        self.db["roles_scopes"].delete_many(filter={})
