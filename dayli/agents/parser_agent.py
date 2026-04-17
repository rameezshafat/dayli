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
    "You are a lifestyle calendar assistant. Convert the user's description of their day "
    "into concrete, non-overlapping calendar events.\n\n"
    "CRITICAL TIME RULE: All events MUST fall within a normal waking day: 06:00 to 23:00. "
    "Never schedule anything between 23:00 and 06:00. "
    "Morning = 07:00-12:00. Afternoon = 12:00-17:00. Evening = 17:00-22:00.\n\n"
    "Default schedule when no times are given:\n"
    "  07:00-07:30  Wake up / Morning routine\n"
    "  07:30-08:00  Breakfast\n"
    "  08:00-12:00  First deep work / study block (morning)\n"
    "  12:00-12:45  Lunch break\n"
    "  12:45-13:15  Short break / reflection\n"
    "  13:15-17:00  Second work / study block (afternoon)\n"
    "  17:00-17:45  Rest\n"
    "  19:00-20:00  Dinner\n"
    "  21:00-22:00  Wind-down\n\n"
    "Rules:\n"
    "1. If user gives explicit times, use them. Otherwise use the defaults above as anchors.\n"
    "2. Expand routine descriptions into ordered blocks starting from 07:00.\n"
    "3. Vague activities ('responsibilities', 'ambassador work') → 1-2 hour block in afternoon.\n"
    "4. Titles: short and clean (e.g. 'DSA Practice', 'Reflection Break', 'Shackleton Work').\n"
    "5. Breaks, rest, meals → flexible: true. Fixed commitments → flexible: false.\n"
    "6. Return at least 5 events covering morning through evening.\n\n"
    "For each event: title, start (ISO 8601 with date), end (ISO 8601 with date), flexible (bool).\n"
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
        user_content = (
            f"Today's date: {today}. All event times must use this date and fall between 06:00 and 23:00.\n\n"
            f"User message: {message}"
        )
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
