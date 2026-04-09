from dataclasses import dataclass, field

from dayli.domain.models.constraint import Constraint


@dataclass(slots=True)
class UserContext:
    user_id: str = "anonymous"
    timezone: str = "UTC"
    constraints: list[Constraint] = field(default_factory=list)
    recent_messages: list[str] = field(default_factory=list)

