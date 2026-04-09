from abc import ABC, abstractmethod

from dayli.domain.models.schedule import ScheduleChangeSet


class CalendarProvider(ABC):
    @abstractmethod
    async def apply_changes(self, user_id: str, changes: ScheduleChangeSet) -> None:
        raise NotImplementedError

