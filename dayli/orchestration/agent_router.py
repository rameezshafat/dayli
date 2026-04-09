from dayli.agents.planner_agent import PlannerAgent
from dayli.core.types import IntentType


class AgentRouter:
    """Resolves which workflow path to use for a user message."""

    def __init__(self, planner: PlannerAgent) -> None:
        self._planner = planner

    async def route(self, message: str) -> IntentType:
        intent = await self._planner.plan(message)
        return intent.intent_type

