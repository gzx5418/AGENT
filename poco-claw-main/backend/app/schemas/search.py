from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class SearchTaskResult(BaseModel):
    session_id: UUID
    title: str | None = None
    status: str
    timestamp: datetime


class SearchProjectResult(BaseModel):
    project_id: UUID
    name: str


class SearchMessageResult(BaseModel):
    message_id: int
    session_id: UUID
    text_preview: str
    timestamp: datetime


class GlobalSearchResponse(BaseModel):
    query: str
    tasks: list[SearchTaskResult] = Field(default_factory=list)
    projects: list[SearchProjectResult] = Field(default_factory=list)
    messages: list[SearchMessageResult] = Field(default_factory=list)
