class LLMClient:
    """Thin abstraction over the selected LLM provider."""

    def __init__(self, model: str) -> None:
        self.model = model

