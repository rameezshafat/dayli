from dayli.domain.models.event import ParsedRequest
from dayli.domain.models.schedule import ScheduleChangeSet


class AuditRepository:
    async def record(
        self,
        user_id: str,
        session_id: str,
        parsed_request: ParsedRequest,
        changes: ScheduleChangeSet,
    ) -> None:
        del user_id, session_id, parsed_request, changes

