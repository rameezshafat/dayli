from dayli.domain.models.event import ParsedRequest
from dayli.domain.models.schedule import ScheduleChangeSet
from dayli.domain.models.user_context import UserContext
from dayli.memory.session_store import SessionStore


class ConversationMemory:
    def __init__(self, session_store: SessionStore) -> None:
        self._session_store = session_store

    async def load(self, user_id: str, session_id: str) -> UserContext:
        return await self._session_store.load(user_id, session_id)

    async def save(
        self,
        user_id: str,
        session_id: str,
        message: str,
        parsed_request: ParsedRequest,
        changes: ScheduleChangeSet,
    ) -> None:
        await self._session_store.save(user_id, session_id, message, changes)

