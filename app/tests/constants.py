"""Unit test constants."""

from app.api.v1.constants import ScopesEnum

CUSTOMER_USER = dict(
    id="65844f12b6de26578d98c2c8",
    scopes=[
        ScopesEnum.AUTH_REFRESH_TOKEN.name,
        ScopesEnum.USERS_GET_ME.name,
        ScopesEnum.USERS_UPDATE_USER.name,
        ScopesEnum.USERS_DELETE_USER.name,
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
        ScopesEnum.COMMENTS_CREATE_COMMENT.name,
        ScopesEnum.COMMENTS_UPDATE_COMMENT.name,
        ScopesEnum.COMMENTS_DELETE_COMMENT.name,
        ScopesEnum.VOTES_GET_VOTE.name,
        ScopesEnum.VOTES_CREATE_VOTE.name,
        ScopesEnum.VOTES_UPDATE_VOTE.name,
        ScopesEnum.VOTES_DELETE_VOTE.name,
    ],
    exp=1703194093,
)

SHOP_SIDE_USER = dict(
    id="659bf67868d14b47475ec11c",
    scopes=[scope.name for scope in ScopesEnum],
    exp=1703194098,
)

USER_NO_SCOPES = dict(id="65844f12b6de26578d98c2c8", scopes=[], exp=1703194093)

DELETED_USER = dict(
    id="659ac89bfe61d8332f6be4c4",
    scopes=[ScopesEnum.AUTH_REFRESH_TOKEN.name],
    exp=1703194093,
)

NOT_VERIFIED_EMAIL_USER = dict(
    id="65ac14f5b9263b2bece37679",
    scopes=[ScopesEnum.AUTH_REFRESH_TOKEN.name, ScopesEnum.USERS_GET_ME.name],
    exp=1703194093,
)

FAKE_USER = dict(
    id="6597f36b349450bbd8e83a52",
    scopes=[ScopesEnum.AUTH_REFRESH_TOKEN.name, ScopesEnum.USERS_GET_ME.name],
    exp=1703203990,
)

TEST_JWT = "someverylongtoken."

FROZEN_DATETIME = "2024-01-06T12:08:35.440000"

REDIS_VERIFICATION_TOKEN = (
    "bec063a47b1be3b091a77a83e821f57cabafce12c1f0dc64f759592935e36fc6"
)

# John1234!
HASHED_PASSWORD = (
    "$argon2id$v=19$m=65536,t=3,p=4$xur1FNnAgDF8GduCsJdqOg$GPwn"
    "/jGlCwyfDVgi+5EDb9uEA+AaP928o20iOL+nQMQ"
)
