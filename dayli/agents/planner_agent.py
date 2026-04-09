from dataclasses import dataclass

from dayli.core.types import IntentType
from dayli.domain.models.user_context import UserContext
from dayli.llm.client import LLMClient


@dataclass(slots=True)
class PlanResult:
    intent_type: IntentType
    summary: str


class PlannerAgent:
    """Classify the request and choose the workflow path."""

    def __init__(self, llm_client: LLMClient) -> None:
        self._llm_client = llm_client

    async def plan(self, message: str, context: UserContext | None = None) -> PlanResult:
        lower_message = message.lower()
        if "move" in lower_message or "tomorrow" in lower_message:
            return PlanResult(intent_type="edit", summary="Edit existing event")
        if "less busy" in lower_message or "lighter" in lower_message:
            return PlanResult(intent_type="rebalance", summary="Rebalance schedule")
        return PlanResult(intent_type="create", summary="Create schedule updates")

