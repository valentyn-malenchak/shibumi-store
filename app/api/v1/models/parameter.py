"""Module that contains parameter domain models."""

from datetime import datetime

from app.api.v1.models import ObjectIdModel


class Parameter(ObjectIdModel):
    """Parameter model."""

    name: str
    machine_name: str
    type: str
    created_at: datetime
    updated_at: datetime | None
