from dayli.domain.models.event import ParsedRequest
from dayli.domain.models.user_context import UserContext


class EditService:
    """Translate soft user instructions into concrete request adjustments."""

    def apply_soft_edits(self, request: ParsedRequest, context: UserContext) -> ParsedRequest:
        del context
        return request

