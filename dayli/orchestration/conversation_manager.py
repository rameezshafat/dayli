from __future__ import annotations

from dayli.agents.calendar_agent import CalendarAgent
from dayli.agents.parser_agent import ParserAgent
from dayli.agents.planner_agent import PlannerAgent
from dayli.agents.response_agent import ResponseAgent
from dayli.agents.validator_agent import ValidatorAgent
from dayli.api.schemas.chat import ChatRequest, ChatResponse
from dayli.core.config import Settings
from dayli.domain.services.conflict_service import ConflictService
from dayli.domain.services.edit_service import EditService
from dayli.domain.services.scheduling_service import SchedulingService
from dayli.llm.client import LLMClient
from dayli.memory.conversation_memory import ConversationMemory
from dayli.memory.session_store import SessionStore
from dayli.repositories.audit_repository import AuditRepository
from dayli.repositories.memory_repository import MemoryRepository
from dayli.repositories.session_repository import SessionRepository
from dayli.tools.calendar.base import CalendarProvider
from dayli.tools.calendar.google import GoogleCalendarProvider


class ConversationManager:
    """Coordinates the full scheduling workflow for each user turn."""

    def __init__(
        self,
        planner: PlannerAgent,
        parser: ParserAgent,
        validator: ValidatorAgent,
        calendar: CalendarAgent,
        responder: ResponseAgent,
        memory: ConversationMemory,
        audit_repository: AuditRepository,
    ) -> None:
        self._planner = planner
        self._parser = parser
        self._validator = validator
        self._calendar = calendar
        self._responder = responder
        self._memory = memory
        self._audit_repository = audit_repository

    @classmethod
    def bootstrap(cls, settings: Settings) -> "ConversationManager":
        llm_client = LLMClient(model=settings.openai_model)
        session_store = SessionStore(SessionRepository(), MemoryRepository())
        memory = ConversationMemory(session_store)
        scheduling_service = SchedulingService()
        conflict_service = ConflictService()
        edit_service = EditService()
        provider: CalendarProvider = GoogleCalendarProvider()

        planner = PlannerAgent(llm_client)
        parser = ParserAgent(llm_client)
        validator = ValidatorAgent(conflict_service, edit_service)
        calendar = CalendarAgent(provider, scheduling_service)
        responder = ResponseAgent(llm_client)

        return cls(
            planner=planner,
            parser=parser,
            validator=validator,
            calendar=calendar,
            responder=responder,
            memory=memory,
            audit_repository=AuditRepository(),
        )

    async def handle_message(self, payload: ChatRequest) -> ChatResponse:
        context = await self._memory.load(payload.user_id, payload.session_id)
        plan = await self._planner.plan(payload.message, context)
        parsed = await self._parser.parse(payload.message, plan, context)
        validated = self._validator.validate(parsed, context)
        changes = await self._calendar.execute(validated, payload.user_id, payload.mode)
        reply = await self._responder.respond(payload.message, plan, validated, changes)
        await self._memory.save(payload.user_id, payload.session_id, payload.message, parsed, changes)
        await self._audit_repository.record(payload.user_id, payload.session_id, parsed, changes)
        return ChatResponse(session_id=payload.session_id, reply=reply, changes=changes)
