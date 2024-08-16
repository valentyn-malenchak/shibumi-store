"""Module that contains comment domain models."""

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, model_validator

from app.api.v1.models import BSONObjectId, ObjectId
from app.utils.pydantic import ObjectIdAnnotation


class Comment(BSONObjectId):
    """Comment model."""

    body: str
    thread_id: Annotated[ObjectId, ObjectIdAnnotation]
    user_id: Annotated[ObjectId, ObjectIdAnnotation]
    parent_comment_id: Annotated[ObjectId, ObjectIdAnnotation] | None
    path: str
    upvotes: int
    downvotes: int
    deleted: bool
    created_at: datetime
    updated_at: datetime | None

    @model_validator(mode="after")
    def handle_deleted(self):
        """Hides body for deleted comments."""
        if self.deleted:
            self.body = "[Deleted]"
        return self


class BaseCommentCreateData(BaseModel):
    """Base comment create data model."""

    thread_id: Annotated[ObjectId, ObjectIdAnnotation]
    body: str
    parent_comment_id: Annotated[ObjectId, ObjectIdAnnotation] | None


class CommentCreateData(BaseModel):
    """Comment create data model."""

    body: str
    user_id: Annotated[ObjectId, ObjectIdAnnotation]
    thread_id: Annotated[ObjectId, ObjectIdAnnotation]
    parent_comment: Comment | None


class CommentUpdateData(BaseModel):
    """Comment update data model."""

    body: str
