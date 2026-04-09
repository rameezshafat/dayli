from dayli.agents.planner_agent import PlanResult
from dayli.domain.models.event import ParsedRequest
from dayli.domain.models.user_context import UserContext
from dayli.llm.client import LLMClient


class ParserAgent:
    """Turn natural language into structured scheduling instructions."""

    def __init__(self, llm_client: LLMClient) -> None:
        self._llm_client = llm_client

    async def parse(
        self,
        message: str,
        plan: PlanResult,
        context: UserContext,
    ) -> ParsedRequest:
        return ParsedRequest.from_message(message=message, intent_type=plan.intent_type, context=context)

