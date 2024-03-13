"""Module that contains role domain models."""

from datetime import datetime

from app.api.v1.constants import RolesEnum
from app.api.v1.models import ListResponseModel, ObjectIdModel


class RoleResponseModel(ObjectIdModel):
    """Role response model."""

    name: str
    machine_name: RolesEnum
    created_at: datetime
    updated_at: datetime | None


class RolesListModel(ListResponseModel):
    """Roles list model."""

    data: list[RoleResponseModel]
