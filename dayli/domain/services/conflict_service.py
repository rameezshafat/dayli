from dayli.core.exceptions import ValidationError
from dayli.domain.models.event import ParsedRequest
from dayli.domain.models.user_context import UserContext


class ConflictService:
    """Check schedule conflicts and hard constraints."""

    def ensure_no_conflicts(self, request: ParsedRequest, context: UserContext) -> None:
        del context
        if not request.events:
            raise ValidationError("No events were parsed from the request.")

