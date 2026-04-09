class SessionRepository:
    async def append_message(self, user_id: str, session_id: str, message: str) -> None:
        del user_id, session_id, message

