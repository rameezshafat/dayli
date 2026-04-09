from dayli.domain.models.event import ParsedRequest
from dayli.domain.models.user_context import UserContext
from dayli.domain.services.conflict_service import ConflictService
from dayli.domain.services.edit_service import EditService


class ValidatorAgent:
    """Run deterministic business rules over parsed scheduling requests."""

    def __init__(self, conflict_service: ConflictService, edit_service: EditService) -> None:
        self._conflict_service = conflict_service
        self._edit_service = edit_service

    def validate(self, parsed_request: ParsedRequest, context: UserContext) -> ParsedRequest:
        adjusted_request = self._edit_service.apply_soft_edits(parsed_request, context)
        self._conflict_service.ensure_no_conflicts(adjusted_request, context)
        return adjusted_request

