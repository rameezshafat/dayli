from pydantic import BaseModel


class SchedulePreviewResponse(BaseModel):
    summary: str

