from dayli.agents.planner_agent import PlanResult
from dayli.domain.models.event import ParsedRequest
from dayli.domain.models.schedule import ScheduleChangeSet
from dayli.llm.client import LLMClient


class ResponseAgent:
    """Generate user-facing responses from validated workflow results."""

    def __init__(self, llm_client: LLMClient) -> None:
        self._llm_client = llm_client

    async def respond(
        self,
        message: str,
        plan: PlanResult,
        parsed_request: ParsedRequest,
        changes: ScheduleChangeSet,
    ) -> str:
        if not changes.events:
            return "I couldn’t find any schedule changes to make yet."
        return f"{plan.summary}: prepared {len(changes.events)} event change(s) in {changes.mode} mode."

