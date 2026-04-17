from __future__ import annotations

import logging
from datetime import datetime

from dayli.agents.planner_agent import PlanResult
from dayli.domain.models.event import ParsedRequest
from dayli.domain.models.schedule import ScheduleChangeSet
from dayli.llm.client import LLMClient

logger = logging.getLogger(__name__)

_SYSTEM = (
    "You are Dayli, a personal scheduling coach. Your reply has two parts:\n\n"
    "1. CONFIRM (1 sentence): briefly name what you've scheduled.\n\n"
    "2. COACH (2-4 sentences): study the specific events listed and the free hours remaining, "
    "then give one concrete, context-aware suggestion.\n\n"
    "HOW TO COACH:\n"
    "- First, mentally categorise every event: deep work, learning/reading, exercise/movement, "
    "meals, rest/recovery, admin, social.\n"
    "- Identify which high-value categories are completely absent.\n"
    "- If there is significant free time (1 h+), suggest filling one gap with the single most "
    "impactful missing activity — e.g. if no reading, suggest a 30-min reading block and name "
    "a good slot; if no movement, suggest a walk or workout and name a slot.\n"
    "- If the day is already packed, flag the biggest risk (no recovery, no meals, etc.) and "
    "suggest a swap or trim.\n"
    "- Be SPECIFIC: name the activity, the duration, and a suggested time slot. "
    "Never give generic advice like 'consider adding breaks'.\n"
    "- If the schedule is genuinely well-rounded, say what's working and offer one stretch upgrade.\n\n"
    "Tone: warm, direct, like a good coach. No fluff. No bullet points — write in flowing sentences."
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
        if changes.operation == "delete":
            return self._delete_confirmation(changes)

        if not changes.events:
            return "I couldn't find any specific events in your message. Could you tell me what you'd like to schedule?"

        action = "added to your calendar" if changes.mode == "apply" else "ready for your review"
        event_lines = "\n".join(
            f"  - {e.title}: {e.start} → {e.end}"
            for e in changes.events
        )
        scheduled_hours = self._scheduled_hours(changes)
        free_hours = max(0.0, 16.0 - scheduled_hours)  # assume 16 waking hours
        user_content = (
            f'User described their day: "{message}"\n\n'
            f"Events {action}:\n{event_lines}\n\n"
            f"Scheduled: {scheduled_hours:.1f} h  |  Free time remaining: {free_hours:.1f} h\n\n"
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

    @staticmethod
    def _scheduled_hours(changes: ScheduleChangeSet) -> float:
        total = 0.0
        for event in changes.events:
            try:
                start = datetime.fromisoformat(event.start)
                end = datetime.fromisoformat(event.end)
                total += (end - start).total_seconds() / 3600
            except (ValueError, TypeError):
                pass
        return total

    def _delete_confirmation(self, changes: ScheduleChangeSet) -> str:
        if changes.mode != "apply":
            if changes.events:
                titles = ", ".join(e.title for e in changes.events[:3])
                return f"Ready to remove {titles} from your calendar. Say 'apply' to confirm."
            return "Ready to clear today's events from your calendar. Say 'apply' to confirm."
        if changes.events:
            titles = ", ".join(e.title for e in changes.events[:3])
            return f"Done — I've removed {titles} from your calendar."
        return "Done — I've cleared today's events from your calendar."

    def _fallback(self, changes: ScheduleChangeSet, plan: PlanResult) -> str:
        titles = ", ".join(e.title for e in changes.events[:3])
        if changes.mode == "apply":
            return f"{plan.summary}. I've added {titles} to your calendar."
        return f"{plan.summary}. Here's a preview of {titles} — say 'apply' to confirm."
