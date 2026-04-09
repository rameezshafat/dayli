from __future__ import annotations

from dataclasses import dataclass, field

from dayli.core.types import IntentType
from dayli.domain.models.user_context import UserContext


@dataclass(slots=True)
class EventRequest:
    title: str
    start: str
    end: str
    flexible: bool = True


@dataclass(slots=True)
class ParsedRequest:
    intent_type: IntentType
    raw_message: str
    events: list[EventRequest] = field(default_factory=list)

    @classmethod
    def from_message(
        cls,
        message: str,
        intent_type: IntentType,
        context: UserContext,
    ) -> "ParsedRequest":
        del context
        return cls(
            intent_type=intent_type,
            raw_message=message,
            events=[
                EventRequest(
                    title="User requested block",
                    start="2026-04-09T09:00:00",
                    end="2026-04-09T10:00:00",
                )
            ],
        )

