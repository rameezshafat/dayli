from __future__ import annotations

import json
import logging
from dataclasses import dataclass

from pydantic import BaseModel

from dayli.core.types import IntentType
from dayli.domain.models.user_context import UserContext
from dayli.llm.client import LLMClient

logger = logging.getLogger(__name__)

_SYSTEM = (
    "You are a scheduling intent classifier. Given a user's message about their daily schedule, "
    "classify the request into exactly one of these intents:\n"
    '- "create": User wants to schedule new events or describe their day — '
    "including vague lifestyle descriptions like 'I spend my morning doing X'\n"
    '- "edit": User wants to modify, move, or reschedule existing events\n'
    '- "rebalance": User wants a lighter or easier day, or to redistribute time blocks\n'
    '- "delete": User wants to remove, cancel, or clear events from their calendar\n'
    '- "clarify": The request is completely unrelated to scheduling\n\n'
    "Important: descriptive routines ('I usually...', 'my day involves...', 'I spend time on...') "
    'are always "create" — never "clarify".\n'
    "Words like 'remove', 'delete', 'cancel', 'clear' always mean \"delete\".\n\n"
    'Respond with valid JSON only: {"intent": "<type>", "summary": "<one sentence>"}'
)


class _Classification(BaseModel):
    intent: str
    summary: str


@dataclass(slots=True)
class PlanResult:
    intent_type: IntentType
    summary: str


class PlannerAgent:
    """Classify the request and choose the workflow path."""

    def __init__(self, llm_client: LLMClient) -> None:
        self._llm_client = llm_client

    async def plan(self, message: str, context: UserContext | None = None) -> PlanResult:
        try:
            response = await self._llm_client.client.chat.completions.create(
                model=self._llm_client.model,
                max_tokens=256,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": _SYSTEM},
                    {"role": "user", "content": message},
                ],
            )
            data = json.loads(response.choices[0].message.content or "{}")
            result = _Classification.model_validate(data)
            valid: set[str] = {"create", "edit", "rebalance", "clarify", "delete"}
            intent_type: IntentType = result.intent if result.intent in valid else "create"  # type: ignore[assignment]
            return PlanResult(intent_type=intent_type, summary=result.summary)
        except Exception as exc:
            logger.warning("LLM planner failed (%s), using heuristic fallback", exc)
            return self._heuristic(message)

    def _heuristic(self, message: str) -> PlanResult:
        lower = message.lower()
        if any(w in lower for w in ("remove", "delete", "cancel", "clear my", "clear all")):
            return PlanResult(intent_type="delete", summary="Delete calendar events")
        if any(w in lower for w in ("move", "tomorrow", "reschedule", "shift")):
            return PlanResult(intent_type="edit", summary="Edit existing event")
        if any(w in lower for w in ("less busy", "lighter", "free up")):
            return PlanResult(intent_type="rebalance", summary="Rebalance schedule")
        return PlanResult(intent_type="create", summary="Create schedule updates")
