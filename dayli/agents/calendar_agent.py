from dayli.domain.models.event import ParsedRequest
from dayli.domain.models.schedule import ScheduleChangeSet
from dayli.domain.services.scheduling_service import SchedulingService
from dayli.tools.calendar.base import CalendarProvider


class CalendarAgent:
    """Execute validated scheduling changes against calendar providers."""

    def __init__(self, provider: CalendarProvider, scheduling_service: SchedulingService) -> None:
        self._provider = provider
        self._scheduling_service = scheduling_service

    async def execute(self, request: ParsedRequest, user_id: str, mode: str) -> ScheduleChangeSet:
        changes = self._scheduling_service.to_change_set(request, mode=mode)
        if mode == "apply":
            await self._provider.apply_changes(user_id=user_id, changes=changes)
        return changes
