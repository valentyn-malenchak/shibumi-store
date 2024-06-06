"""Module that contains role domain models."""

from datetime import datetime

from app.api.v1.constants import RolesEnum
from app.api.v1.models import BSONObjectId, List


class Role(BSONObjectId):
    """Role model."""

    name: str
    machine_name: RolesEnum
    created_at: datetime
    updated_at: datetime | None


class RoleList(List):
    """Role list model."""

    data: list[Role]
