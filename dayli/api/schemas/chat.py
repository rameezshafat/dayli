from pydantic import BaseModel, Field

from dayli.domain.models.schedule import ScheduleChangeSet


class ChatRequest(BaseModel):
    user_id: str
    session_id: str
    message: str = Field(min_length=1)
    mode: str = "preview"
    event_ids: list[str] | None = None   # selected event IDs for targeted delete


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    changes: ScheduleChangeSet

