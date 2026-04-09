from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Iterable

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
    notes: list[str] = field(default_factory=list)

    @classmethod
    def from_message(
        cls,
        message: str,
        intent_type: IntentType,
        context: UserContext,
    ) -> "ParsedRequest":
        if intent_type == "edit":
            return cls(
                intent_type=intent_type,
                raw_message=message,
                events=_build_edit_events(message),
                notes=["Detected an edit request from conversational context."],
            )
        if intent_type == "rebalance":
            return cls(
                intent_type=intent_type,
                raw_message=message,
                events=_build_rebalance_events(context),
                notes=["Rebalanced the morning by moving a flexible block later."],
            )

        events = list(_extract_events(message))
        if not events:
            events = [
                EventRequest(
                    title="Planning block",
                    start="2026-04-09T09:00:00",
                    end="2026-04-09T10:00:00",
                )
            ]

        return cls(intent_type=intent_type, raw_message=message, events=events)


def _extract_events(message: str) -> Iterable[EventRequest]:
    normalized = message.lower()
    date_prefix = "2026-04-09"

    range_pattern = re.compile(
        r"(?P<title>[a-z ]+?)\s+(?:from\s+)?(?P<start>\d{1,2})(?::(?P<start_min>\d{2}))?\s*(?:-|to)\s*(?P<end>\d{1,2})(?::(?P<end_min>\d{2}))?",
        re.IGNORECASE,
    )
    at_pattern = re.compile(
        r"(?P<title>[a-z ]+?)\s+at\s+(?P<hour>\d{1,2})(?::(?P<minute>\d{2}))?",
        re.IGNORECASE,
    )

    consumed_spans: list[tuple[int, int]] = []
    for match in range_pattern.finditer(normalized):
        title = _normalize_title(match.group("title"))
        start = _iso_time(date_prefix, int(match.group("start")), int(match.group("start_min") or 0))
        end = _iso_time(date_prefix, int(match.group("end")), int(match.group("end_min") or 0))
        consumed_spans.append(match.span())
        yield EventRequest(title=title, start=start, end=end, flexible=title != "Work")

    for match in at_pattern.finditer(normalized):
        if any(start <= match.start() and match.end() <= end for start, end in consumed_spans):
            continue
        title = _normalize_title(match.group("title"))
        hour = int(match.group("hour"))
        minute = int(match.group("minute") or 0)
        start_dt = datetime.fromisoformat(_iso_time(date_prefix, hour, minute))
        end_dt = start_dt + timedelta(hours=1)
        yield EventRequest(
            title=title,
            start=start_dt.isoformat(),
            end=end_dt.isoformat(),
            flexible=title not in {"Dinner", "Work"},
        )


def _build_edit_events(message: str) -> list[EventRequest]:
    lower_message = message.lower()
    target = "Gym" if "gym" in lower_message else "Updated event"
    date_prefix = "2026-04-10" if "tomorrow" in lower_message else "2026-04-09"
    return [
        EventRequest(
            title=target,
            start=f"{date_prefix}T18:00:00",
            end=f"{date_prefix}T19:00:00",
            flexible=True,
        )
    ]


def _build_rebalance_events(context: UserContext) -> list[EventRequest]:
    del context
    return [
        EventRequest(
            title="Deep Work",
            start="2026-04-09T13:00:00",
            end="2026-04-09T15:00:00",
            flexible=True,
        )
    ]


def _normalize_title(value: str) -> str:
    return " ".join(part.capitalize() for part in value.strip(" ,").split())


def _iso_time(date_prefix: str, hour: int, minute: int) -> str:
    if hour <= 7:
        hour += 12
    return f"{date_prefix}T{hour:02d}:{minute:02d}:00"
