from dayli.domain.models.schedule import ScheduleChangeSet
from dayli.tools.calendar.base import CalendarProvider


class OutlookCalendarProvider(CalendarProvider):
    async def apply_changes(self, user_id: str, changes: ScheduleChangeSet) -> None:
        del user_id, changes

