"""Contains a migration that inserts/deletes roles."""

import arrow
from mongodb_migrations.base import BaseMigration

from app.api.v1.constants import RolesEnum, ScopesEnum
from app.services.mongo.constants import MongoCollectionsEnum


class Migration(BaseMigration):  # type: ignore
    """Migration that inserts/deletes roles."""

    @staticmethod
    def __decompose_snake_case(string: str) -> str:
        """Decomposes snake case."""

        words = [word.title() for word in string.split("_")]

        return " ".join(words)

    def upgrade(self) -> None:
        """Inserts roles."""
        self.db[MongoCollectionsEnum.ROLES].insert_many(
            [
                {
                    "name": self.__decompose_snake_case(RolesEnum.CUSTOMER),
                    "machine_name": RolesEnum.CUSTOMER,
                    "scopes": [
                        ScopesEnum.AUTH_REFRESH_TOKEN.name,
                        ScopesEnum.USERS_GET_ME.name,
                        ScopesEnum.USERS_UPDATE_USER.name,
                        ScopesEnum.USERS_UPDATE_USER_PASSWORD.name,
                        ScopesEnum.USERS_DELETE_USER.name,
                        ScopesEnum.ROLES_GET_ROLES.name,
                        ScopesEnum.CATEGORIES_GET_CATEGORIES.name,
                        ScopesEnum.CATEGORIES_GET_CATEGORY.name,
                        ScopesEnum.CATEGORIES_GET_CATEGORY_PARAMETERS.name,
                        ScopesEnum.PRODUCTS_GET_PRODUCTS.name,
                        ScopesEnum.PRODUCTS_GET_PRODUCT.name,
                        ScopesEnum.CARTS_GET_CART.name,
                        ScopesEnum.CARTS_ADD_PRODUCT.name,
                        ScopesEnum.CARTS_UPDATE_PRODUCT.name,
                        ScopesEnum.CARTS_DELETE_PRODUCT.name,
                        ScopesEnum.THREADS_GET_THREAD.name,
                        ScopesEnum.COMMENTS_GET_COMMENT.name,
                        ScopesEnum.COMMENTS_CREATE_COMMENT.name,
                        ScopesEnum.COMMENTS_UPDATE_COMMENT.name,
                        ScopesEnum.COMMENTS_DELETE_COMMENT.name,
                        ScopesEnum.VOTES_GET_VOTE.name,
                        ScopesEnum.VOTES_CREATE_VOTE.name,
                        ScopesEnum.VOTES_UPDATE_VOTE.name,
                        ScopesEnum.VOTES_DELETE_VOTE.name,
                    ],
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "name": self.__decompose_snake_case(RolesEnum.SUPPORT),
                    "machine_name": RolesEnum.SUPPORT,
                    "scopes": [
                        ScopesEnum.AUTH_REFRESH_TOKEN.name,
                        ScopesEnum.USERS_GET_ME.name,
                        ScopesEnum.USERS_GET_USERS.name,
                        ScopesEnum.USERS_GET_USER.name,
                        ScopesEnum.USERS_CREATE_USER.name,
                        ScopesEnum.USERS_UPDATE_USER.name,
                        ScopesEnum.USERS_UPDATE_USER_PASSWORD.name,
                        ScopesEnum.USERS_DELETE_USER.name,
                        ScopesEnum.ROLES_GET_ROLES.name,
                        ScopesEnum.CATEGORIES_GET_CATEGORIES.name,
                        ScopesEnum.CATEGORIES_GET_CATEGORY.name,
                        ScopesEnum.CATEGORIES_GET_CATEGORY_PARAMETERS.name,
                        ScopesEnum.PRODUCTS_GET_PRODUCTS.name,
                        ScopesEnum.PRODUCTS_GET_PRODUCT.name,
                        ScopesEnum.CARTS_GET_CART.name,
                        ScopesEnum.CARTS_ADD_PRODUCT.name,
                        ScopesEnum.CARTS_UPDATE_PRODUCT.name,
                        ScopesEnum.CARTS_DELETE_PRODUCT.name,
                        ScopesEnum.THREADS_GET_THREAD.name,
                        ScopesEnum.THREADS_CREATE_THREAD.name,
                        ScopesEnum.THREADS_UPDATE_THREAD.name,
                        ScopesEnum.COMMENTS_GET_COMMENT.name,
                        ScopesEnum.COMMENTS_CREATE_COMMENT.name,
                        ScopesEnum.COMMENTS_UPDATE_COMMENT.name,
                        ScopesEnum.COMMENTS_DELETE_COMMENT.name,
                        ScopesEnum.VOTES_GET_VOTE.name,
                        ScopesEnum.VOTES_CREATE_VOTE.name,
                        ScopesEnum.VOTES_UPDATE_VOTE.name,
                        ScopesEnum.VOTES_DELETE_VOTE.name,
                    ],
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "name": self.__decompose_snake_case(RolesEnum.WAREHOUSE_STUFF),
                    "machine_name": RolesEnum.WAREHOUSE_STUFF,
                    "scopes": [
                        ScopesEnum.AUTH_REFRESH_TOKEN.name,
                        ScopesEnum.USERS_GET_ME.name,
                        ScopesEnum.USERS_UPDATE_USER_PASSWORD.name,
                        ScopesEnum.ROLES_GET_ROLES.name,
                        ScopesEnum.CATEGORIES_GET_CATEGORIES.name,
                        ScopesEnum.CATEGORIES_GET_CATEGORY.name,
                        ScopesEnum.CATEGORIES_GET_CATEGORY_PARAMETERS.name,
                        ScopesEnum.PRODUCTS_GET_PRODUCTS.name,
                        ScopesEnum.PRODUCTS_GET_PRODUCT.name,
                        ScopesEnum.PRODUCTS_CREATE_PRODUCT.name,
                        ScopesEnum.PRODUCTS_UPDATE_PRODUCT.name,
                        ScopesEnum.CARTS_GET_CART.name,
                        ScopesEnum.CARTS_ADD_PRODUCT.name,
                        ScopesEnum.CARTS_UPDATE_PRODUCT.name,
                        ScopesEnum.CARTS_DELETE_PRODUCT.name,
                        ScopesEnum.THREADS_GET_THREAD.name,
                        ScopesEnum.COMMENTS_GET_COMMENT.name,
                    ],
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "name": self.__decompose_snake_case(RolesEnum.CONTENT_MANAGER),
                    "machine_name": RolesEnum.CONTENT_MANAGER,
                    "scopes": [
                        ScopesEnum.AUTH_REFRESH_TOKEN.name,
                        ScopesEnum.USERS_GET_ME.name,
                        ScopesEnum.USERS_UPDATE_USER_PASSWORD.name,
                        ScopesEnum.ROLES_GET_ROLES.name,
                        ScopesEnum.CATEGORIES_GET_CATEGORIES.name,
                        ScopesEnum.CATEGORIES_GET_CATEGORY.name,
                        ScopesEnum.CATEGORIES_GET_CATEGORY_PARAMETERS.name,
                        ScopesEnum.PRODUCTS_GET_PRODUCTS.name,
                        ScopesEnum.PRODUCTS_GET_PRODUCT.name,
                        ScopesEnum.PRODUCTS_UPDATE_PRODUCT.name,
                        ScopesEnum.CARTS_GET_CART.name,
                        ScopesEnum.CARTS_ADD_PRODUCT.name,
                        ScopesEnum.CARTS_UPDATE_PRODUCT.name,
                        ScopesEnum.CARTS_DELETE_PRODUCT.name,
                        ScopesEnum.THREADS_GET_THREAD.name,
                        ScopesEnum.COMMENTS_GET_COMMENT.name,
                    ],
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "name": self.__decompose_snake_case(RolesEnum.MARKETING_MANAGER),
                    "machine_name": RolesEnum.MARKETING_MANAGER,
                    "scopes": [
                        ScopesEnum.AUTH_REFRESH_TOKEN.name,
                        ScopesEnum.USERS_GET_ME.name,
                        ScopesEnum.USERS_UPDATE_USER_PASSWORD.name,
                        ScopesEnum.ROLES_GET_ROLES.name,
                        ScopesEnum.CATEGORIES_GET_CATEGORIES.name,
                        ScopesEnum.CATEGORIES_GET_CATEGORY.name,
                        ScopesEnum.CATEGORIES_GET_CATEGORY_PARAMETERS.name,
                        ScopesEnum.PRODUCTS_GET_PRODUCTS.name,
                        ScopesEnum.PRODUCTS_GET_PRODUCT.name,
                        ScopesEnum.CARTS_GET_CART.name,
                        ScopesEnum.CARTS_ADD_PRODUCT.name,
                        ScopesEnum.CARTS_UPDATE_PRODUCT.name,
                        ScopesEnum.CARTS_DELETE_PRODUCT.name,
                        ScopesEnum.THREADS_GET_THREAD.name,
                        ScopesEnum.COMMENTS_GET_COMMENT.name,
                    ],
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
                {
                    "name": self.__decompose_snake_case(RolesEnum.ADMIN),
                    "machine_name": RolesEnum.ADMIN,
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
                        ScopesEnum.ROLES_GET_ROLES.name,
                        ScopesEnum.CATEGORIES_GET_CATEGORIES.name,
                        ScopesEnum.CATEGORIES_GET_CATEGORY.name,
                        ScopesEnum.CATEGORIES_GET_CATEGORY_PARAMETERS.name,
                        ScopesEnum.PRODUCTS_GET_PRODUCTS.name,
                        ScopesEnum.PRODUCTS_GET_PRODUCT.name,
                        ScopesEnum.PRODUCTS_CREATE_PRODUCT.name,
                        ScopesEnum.PRODUCTS_UPDATE_PRODUCT.name,
                        ScopesEnum.CARTS_GET_CART.name,
                        ScopesEnum.CARTS_ADD_PRODUCT.name,
                        ScopesEnum.CARTS_UPDATE_PRODUCT.name,
                        ScopesEnum.CARTS_DELETE_PRODUCT.name,
                        ScopesEnum.THREADS_GET_THREAD.name,
                        ScopesEnum.THREADS_CREATE_THREAD.name,
                        ScopesEnum.THREADS_UPDATE_THREAD.name,
                        ScopesEnum.COMMENTS_GET_COMMENT.name,
                        ScopesEnum.COMMENTS_CREATE_COMMENT.name,
                        ScopesEnum.COMMENTS_UPDATE_COMMENT.name,
                        ScopesEnum.COMMENTS_DELETE_COMMENT.name,
                        ScopesEnum.VOTES_GET_VOTE.name,
                        ScopesEnum.VOTES_CREATE_VOTE.name,
                        ScopesEnum.VOTES_UPDATE_VOTE.name,
                        ScopesEnum.VOTES_DELETE_VOTE.name,
                    ],
                    "created_at": arrow.utcnow().datetime,
                    "updated_at": None,
                },
            ]
        )

    def downgrade(self) -> None:
        """Drops roles."""
        self.db[MongoCollectionsEnum.ROLES].delete_many(filter={})
