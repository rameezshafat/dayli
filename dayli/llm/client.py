from openai import AsyncOpenAI


class LLMClient:
    """Thin abstraction over a local Ollama model (OpenAI-compatible endpoint)."""

    def __init__(self, model: str, base_url: str) -> None:
        self.model = model
        self.client = AsyncOpenAI(
            api_key="ollama",  # Ollama ignores the key; openai SDK requires non-empty
            base_url=base_url,
        )
