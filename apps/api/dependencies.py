"""Shared FastAPI dependencies."""

from dayli.core.config import Settings, get_settings
from dayli.orchestration.conversation_manager import ConversationManager


def get_conversation_manager() -> ConversationManager:
    settings = get_settings()
    return ConversationManager.bootstrap(settings)


def get_app_settings() -> Settings:
    return get_settings()

