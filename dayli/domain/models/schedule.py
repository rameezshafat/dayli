from dataclasses import dataclass, field


@dataclass(slots=True)
class ScheduledEvent:
    title: str
    start: str
    end: str
    event_id: str | None = None


@dataclass(slots=True)
class ScheduleChangeSet:
    mode: str = "preview"
    operation: str = "add"          # "add" | "delete"
    events: list[ScheduledEvent] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

