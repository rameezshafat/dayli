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
        del message, parsed_request
        if not changes.events:
            return "I couldn’t find any schedule changes to make yet."
        titles = ", ".join(event.title for event in changes.events[:3])
        if changes.mode == "apply":
            return f"{plan.summary}. I updated {titles} on your calendar."
        return f"{plan.summary}. I prepared {titles} for review in preview mode."
