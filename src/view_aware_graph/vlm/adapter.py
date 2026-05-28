"""Provider-neutral adapter protocol for VLM implementations."""

from __future__ import annotations

from typing import Protocol

from view_aware_graph.vlm.types import VLMRequest, VLMResponse


class VLMAdapter(Protocol):
    """Protocol implemented by concrete local or hosted VLM adapters."""

    @property
    def provider(self) -> str:
        """Provider identifier, such as `ollama` or a hosted API name."""
        ...

    @property
    def model(self) -> str:
        """Configured model identifier."""
        ...

    def generate(self, request: VLMRequest) -> VLMResponse:
        """Run a VLM request and return the raw provider response."""
        ...
