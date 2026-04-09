from dayli.domain.models.schedule import ScheduleChangeSet
from dayli.domain.models.user_context import UserContext


class MemoryRepository:
    async def load_context(self, user_id: str, session_id: str) -> UserContext:
        return UserContext(user_id=user_id, recent_messages=[f"session:{session_id}"])

    async def save_changes(self, user_id: str, session_id: str, changes: ScheduleChangeSet) -> None:
        del user_id, session_id, changes

