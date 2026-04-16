from __future__ import annotations

import json
import logging
from datetime import date

from pydantic import BaseModel

from dayli.agents.planner_agent import PlanResult
from dayli.domain.models.event import EventRequest, ParsedRequest
from dayli.domain.models.user_context import UserContext
from dayli.llm.client import LLMClient

logger = logging.getLogger(__name__)

_SYSTEM = (
    "You are a calendar event extractor. Extract all events from the user's message.\n"
    "For each event provide:\n"
    "- title: clean event name (e.g. 'Gym', 'Work', 'Team Meeting')\n"
    "- start: ISO 8601 datetime (e.g. '2026-04-14T09:00:00')\n"
    "- end: ISO 8601 datetime\n"
    "- flexible: true if the event can be rescheduled, false if fixed\n\n"
    "If no time is mentioned, use sensible defaults (gym=07:00-08:00, work=09:00-17:00, dinner=19:00-20:00).\n"
    'Respond with valid JSON only: {"events": [...], "notes": [...]}'
)


class _EventItem(BaseModel):
    title: str
    start: str
    end: str
    flexible: bool = True


class _ParsedEvents(BaseModel):
    events: list[_EventItem]
    notes: list[str] = []


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
        today = date.today().isoformat()
        user_content = f"Today's date: {today}\n\nUser message: {message}"
        try:
            response = await self._llm_client.client.chat.completions.create(
                model=self._llm_client.model,
                max_tokens=1024,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": _SYSTEM},
                    {"role": "user", "content": user_content},
                ],
            )
            data = json.loads(response.choices[0].message.content or "{}")
            result = _ParsedEvents.model_validate(data)
            events = [
                EventRequest(title=e.title, start=e.start, end=e.end, flexible=e.flexible)
                for e in result.events
            ]
            return ParsedRequest(
                intent_type=plan.intent_type,
                raw_message=message,
                events=events,
                notes=result.notes,
            )
        except Exception as exc:
            logger.warning("LLM parser failed (%s), using regex fallback", exc)
            return ParsedRequest.from_message(
                message=message, intent_type=plan.intent_type, context=context
            )
