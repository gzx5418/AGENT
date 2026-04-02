from datetime import datetime

from pydantic import BaseModel


class UserInputRequestCreateRequest(BaseModel):
    session_id: str
    tool_name: str
    tool_input: dict
    expires_at: datetime | None = None


class UserInputRequestResponse(BaseModel):
    id: str
    session_id: str
    tool_name: str
    tool_input: dict
    status: str
    answers: dict | None = None
    expires_at: datetime
    answered_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
