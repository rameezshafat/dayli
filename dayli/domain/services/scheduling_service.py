from dayli.domain.models.event import ParsedRequest
from dayli.domain.models.schedule import ScheduleChangeSet, ScheduledEvent


class SchedulingService:
    """Build provider-neutral schedule changes from parsed requests."""

    def to_change_set(self, request: ParsedRequest) -> ScheduleChangeSet:
        return ScheduleChangeSet(
            events=[
                ScheduledEvent(title=event.title, start=event.start, end=event.end)
                for event in request.events
            ]
        )

