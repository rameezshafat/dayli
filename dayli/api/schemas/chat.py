from pydantic import BaseModel, Field

from dayli.domain.models.schedule import ScheduleChangeSet


class ChatRequest(BaseModel):
    user_id: str
    session_id: str
    message: str = Field(min_length=1)
    mode: str = "preview"


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    changes: ScheduleChangeSet

