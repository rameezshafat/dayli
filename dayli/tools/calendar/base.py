from abc import ABC, abstractmethod

from dayli.domain.models.schedule import ScheduleChangeSet, ScheduledEvent


class CalendarProvider(ABC):
    @abstractmethod
    async def apply_changes(self, user_id: str, changes: ScheduleChangeSet) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete_events(self, user_id: str, changes: ScheduleChangeSet) -> int:
        """Delete matching events. Returns count of deleted events."""
        raise NotImplementedError

    @abstractmethod
    async def list_events(self, user_id: str) -> list[ScheduledEvent]:
        """List today's calendar events."""
        raise NotImplementedError

