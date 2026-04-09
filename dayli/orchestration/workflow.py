from dataclasses import dataclass

from dayli.domain.models.event import ParsedRequest
from dayli.domain.models.schedule import ScheduleChangeSet


@dataclass(slots=True)
class WorkflowResult:
    reply: str
    changes: ScheduleChangeSet
    parsed_request: ParsedRequest

