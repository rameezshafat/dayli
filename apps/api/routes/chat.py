from fastapi import APIRouter, Depends

from apps.api.dependencies import get_conversation_manager
from dayli.api.schemas.chat import ChatRequest, ChatResponse
from dayli.orchestration.conversation_manager import ConversationManager

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    manager: ConversationManager = Depends(get_conversation_manager),
) -> ChatResponse:
    return await manager.handle_message(payload)

