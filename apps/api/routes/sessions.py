from fastapi import APIRouter

router = APIRouter(tags=["sessions"])


@router.get("/sessions/{session_id}")
async def get_session(session_id: str) -> dict[str, str]:
    return {"session_id": session_id, "status": "stub"}

