from openai import AsyncOpenAI

_GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"


class LLMClient:
    """Thin abstraction over the LLM provider (Gemini via OpenAI-compatible endpoint)."""

    def __init__(self, model: str, api_key: str) -> None:
        self.model = model
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=_GEMINI_BASE_URL,
        )
