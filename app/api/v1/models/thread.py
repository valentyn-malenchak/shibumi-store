"""Module that contains thread domain models."""

from datetime import datetime

from app.api.v1.models import BSONObjectId


class Thread(BSONObjectId):
    """Thread model."""

    created_at: datetime
    updated_at: datetime | None
