from dayli.domain.models.schedule import ScheduleChangeSet
from dayli.domain.models.user_context import UserContext
from dayli.repositories.memory_repository import MemoryRepository
from dayli.repositories.session_repository import SessionRepository


class SessionStore:
    def __init__(
        self,
        session_repository: SessionRepository,
        memory_repository: MemoryRepository,
    ) -> None:
        self._session_repository = session_repository
        self._memory_repository = memory_repository

    async def load(self, user_id: str, session_id: str) -> UserContext:
        return await self._memory_repository.load_context(user_id, session_id)

    async def save(
        self,
        user_id: str,
        session_id: str,
        message: str,
        changes: ScheduleChangeSet,
    ) -> None:
        await self._session_repository.append_message(user_id, session_id, message)
        await self._memory_repository.save_changes(user_id, session_id, changes)

