"""Module that contains thread domain models."""

from datetime import datetime

from pydantic import BaseModel

from app.api.v1.models import BSONObjectId


class Thread(BSONObjectId):
    """Thread model."""

    name: str
    body: str
    created_at: datetime
    updated_at: datetime | None


class ThreadCreateData(BaseModel):
    """Thread create data model."""

    name: str
    body: str
