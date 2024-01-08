"""Unit test constants."""

from app.api.v1.constants import ScopesEnum

CUSTOMER_USER = dict(
    id="65844f12b6de26578d98c2c8",
    scopes=[
        ScopesEnum.AUTH_REFRESH_TOKEN.name,
        ScopesEnum.USERS_GET_ME.name,
        ScopesEnum.USERS_UPDATE_USERS.name,
        ScopesEnum.USERS_DELETE_USERS.name,
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

FAKE_USER = dict(
    id="6597f36b349450bbd8e83a52",
    scopes=[],
    exp=1703203990,
)

TEST_JWT = "someverylongtoken."

FROZEN_DATETIME = "2024-01-05T12:08:35.440000"
