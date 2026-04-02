from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UserInputRequestCreateRequest(BaseModel):
    session_id: UUID
    tool_name: str
    tool_input: dict
    expires_at: datetime | None = None


class UserInputAnswerRequest(BaseModel):
    answers: dict[str, str]


class UserInputRequestResponse(BaseModel):
    id: UUID
    session_id: UUID
    tool_name: str
    tool_input: dict
    status: str
    answers: dict | None = None
    expires_at: datetime
    answered_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
