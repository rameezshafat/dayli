from dataclasses import dataclass, field


@dataclass(slots=True)
class ScheduledEvent:
    title: str
    start: str
    end: str


@dataclass(slots=True)
class ScheduleChangeSet:
    mode: str = "preview"
    events: list[ScheduledEvent] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

