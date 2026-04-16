from __future__ import annotations

import logging

from dayli.agents.planner_agent import PlanResult
from dayli.domain.models.event import ParsedRequest
from dayli.domain.models.schedule import ScheduleChangeSet
from dayli.llm.client import LLMClient

logger = logging.getLogger(__name__)

_SYSTEM = (
    "You are Dayli, a friendly AI scheduling assistant. "
    "Generate a brief, warm, conversational reply confirming the schedule changes. "
    "Mention the key events by name. Be concise — 1-3 sentences max. "
    "If no events were found, gently ask the user to clarify."
)


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
            return "I couldn't find any specific events in your message. Could you tell me what you'd like to schedule?"

        event_list = ", ".join(e.title for e in changes.events[:5])
        action = "added to your calendar" if changes.mode == "apply" else "ready for your review"
        user_content = (
            f'User said: "{message}"\n'
            f"Events {action}: {event_list}\n"
            f"Intent: {plan.summary}"
        )

        try:
            response = await self._llm_client.client.chat.completions.create(
                model=self._llm_client.model,
                max_tokens=256,
                messages=[
                    {"role": "system", "content": _SYSTEM},
                    {"role": "user", "content": user_content},
                ],
            )
            return response.choices[0].message.content or self._fallback(changes, plan)
        except Exception as exc:
            logger.warning("LLM responder failed (%s), using fallback", exc)
            return self._fallback(changes, plan)

    def _fallback(self, changes: ScheduleChangeSet, plan: PlanResult) -> str:
        titles = ", ".join(e.title for e in changes.events[:3])
        if changes.mode == "apply":
            return f"{plan.summary}. I've added {titles} to your calendar."
        return f"{plan.summary}. Here's a preview of {titles} — say 'apply' to confirm."
