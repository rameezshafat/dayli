from __future__ import annotations

from dayli.domain.models.event import ParsedRequest
from dayli.domain.models.schedule import ScheduleChangeSet, ScheduledEvent
from dayli.domain.services.scheduling_service import SchedulingService
from dayli.tools.calendar.base import CalendarProvider


class CalendarAgent:
    """Execute validated scheduling changes against calendar providers."""

    def __init__(self, provider: CalendarProvider, scheduling_service: SchedulingService) -> None:
        self._provider = provider
        self._scheduling_service = scheduling_service

    async def execute(
        self,
        request: ParsedRequest,
        user_id: str,
        mode: str,
        event_ids: list[str] | None = None,
    ) -> ScheduleChangeSet:
        changes = self._scheduling_service.to_change_set(request, mode=mode)

        if changes.operation == "delete":
            if mode == "preview":
                # Populate events from the live calendar so the UI can show them
                try:
                    live_events = await self._provider.list_events(user_id=user_id)
                    changes.events = live_events
                except Exception:
                    pass  # leave events empty — UI will still show the delete confirmation
            else:
                # Apply: if the frontend passed specific IDs, build the events list from them
                if event_ids:
                    changes.events = [
                        ScheduledEvent(title="", start="", end="", event_id=eid)
                        for eid in event_ids
                    ]
                await self._provider.delete_events(user_id=user_id, changes=changes)
        elif mode == "apply":
            await self._provider.apply_changes(user_id=user_id, changes=changes)

        return changes
