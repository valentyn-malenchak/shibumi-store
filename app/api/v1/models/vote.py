"""Module that contains vote domain models."""

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel

from app.api.v1.models import BSONObjectId, ObjectId
from app.utils.pydantic import ObjectIdAnnotation


class Vote(BSONObjectId):
    """Vote model."""

    value: bool
    comment_id: Annotated[ObjectId, ObjectIdAnnotation]
    user_id: Annotated[ObjectId, ObjectIdAnnotation]
    created_at: datetime
    updated_at: datetime | None


class VoteData(BaseModel):
    """Vote data model."""

    value: bool


class BaseVoteCreateData(BaseModel):
    """Base vote create data model."""

    comment_id: Annotated[ObjectId, ObjectIdAnnotation]
    value: bool


class VoteCreateData(BaseModel):
    """Vote create data model."""

    value: bool
    user_id: Annotated[ObjectId, ObjectIdAnnotation]
    comment_id: Annotated[ObjectId, ObjectIdAnnotation]
