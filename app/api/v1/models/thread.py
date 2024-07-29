"""Module that contains thread domain models."""

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel

from app.api.v1.models import BSONObjectId, ObjectId
from app.utils.pydantic import ObjectIdAnnotation


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


class Comment(BSONObjectId):
    """Thread comment model."""

    body: str
    thread_id: Annotated[ObjectId, ObjectIdAnnotation]
    author_id: Annotated[ObjectId, ObjectIdAnnotation]
    parent_comment_id: Annotated[ObjectId, ObjectIdAnnotation] | None
    path: str
    upvotes: int
    downvotes: int
    created_at: datetime
    updated_at: datetime | None


class BaseCommentCreateData(BaseModel):
    """Base thread comment create data model."""

    body: str
    parent_comment_id: Annotated[ObjectId, ObjectIdAnnotation] | None


class CommentCreateData(BaseModel):
    """Thread comment create data model."""

    body: str
    author_id: Annotated[ObjectId, ObjectIdAnnotation]
    thread_id: Annotated[ObjectId, ObjectIdAnnotation]
    parent_comment: Comment | None


class CommentUpdateData(BaseModel):
    """Thread comment update data model."""

    body: str


class Vote(BSONObjectId):
    """Thread comment vote model."""

    value: bool
    comment_id: Annotated[ObjectId, ObjectIdAnnotation]
    user_id: Annotated[ObjectId, ObjectIdAnnotation]
    created_at: datetime
    updated_at: datetime | None


class BaseVoteData(BaseModel):
    """Base vote data model."""

    value: bool


class VoteCreateData(BaseModel):
    """Vote create data model."""

    value: bool
    user_id: Annotated[ObjectId, ObjectIdAnnotation]
    comment_id: Annotated[ObjectId, ObjectIdAnnotation]


class VoteUpdateData(BaseModel):
    """Vote update data."""

    value: bool
    vote_id: Annotated[ObjectId, ObjectIdAnnotation]
    comment_id: Annotated[ObjectId, ObjectIdAnnotation]
