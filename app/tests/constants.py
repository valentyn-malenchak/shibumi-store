"""Unit test constants."""

from app.api.v1.constants import ScopesEnum

USER = dict(
    id="65844f12b6de26578d98c2c8",
    scopes=[scope.name for scope in ScopesEnum],
    exp=1703194093,
)

USER_NO_SCOPES = dict(id="65844f12b6de26578d98c2c8", scopes=[], exp=1703194093)

FAKE_USER = dict(
    id="6597f36b349450bbd8e83a52",
    scopes=[scope.name for scope in ScopesEnum],
    exp=1703203990,
)

JWT = "someverylongtoken."

FROZEN_DATETIME = "2024-01-05T12:08:35.440000"
