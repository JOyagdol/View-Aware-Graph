"""Local Ollama VLM adapter."""

from __future__ import annotations

import base64
import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any, cast
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from view_aware_graph.vlm.types import (
    RetryPolicy,
    VLMAdapterError,
    VLMRequest,
    VLMResponse,
    build_failure_report,
)

OllamaTransport = Callable[[bytes], bytes]


@dataclass(frozen=True)
class OllamaAdapter:
    """Concrete adapter for Ollama's `/api/generate` vision endpoint."""

    model: str
    endpoint: str
    temperature: float = 0.0
    retry_policy: RetryPolicy = RetryPolicy(max_retries=0)
    timeout_seconds: float = 120.0
    transport: OllamaTransport | None = None

    @property
    def provider(self) -> str:
        """Provider identifier."""

        return "ollama"

    def generate(self, request: VLMRequest) -> VLMResponse:
        """Send an image prompt to Ollama and return the raw response."""

        payload = build_ollama_generate_payload(
            model=self.model,
            prompt=request.prompt,
            image_bytes=request.image_path.read_bytes(),
            temperature=self.temperature,
        )
        payload_bytes = json.dumps(payload).encode("utf-8")
        attempts = 0

        while attempts < self.retry_policy.max_attempts:
            attempts += 1
            try:
                raw_bytes = self._post(payload_bytes)
            except TimeoutError as exc:
                self._raise_or_retry(request, "timeout", str(exc), attempts)
            except HTTPError as exc:
                error_type = _http_error_type(exc.code)
                self._raise_or_retry(request, error_type, str(exc), attempts)
            except URLError as exc:
                self._raise_or_retry(request, "connection_error", str(exc.reason), attempts)
            else:
                raw_text = raw_bytes.decode("utf-8")
                return VLMResponse(
                    provider=self.provider,
                    model=self.model,
                    raw_text=raw_text,
                    graph_text=extract_ollama_response_text(raw_text),
                    metadata={"attempts": attempts, "endpoint": self.endpoint},
                )

        raise AssertionError("unreachable retry loop state")

    def _post(self, payload: bytes) -> bytes:
        if self.transport is not None:
            return self.transport(payload)

        request = Request(
            self.endpoint,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request, timeout=self.timeout_seconds) as response:
            return cast(bytes, response.read())

    def _raise_or_retry(
        self,
        request: VLMRequest,
        error_type: str,
        message: str,
        attempts: int,
    ) -> None:
        failure = build_failure_report(
            provider=self.provider,
            model=self.model,
            request=request,
            error_type=error_type,
            message=message,
            attempts=attempts,
            retry_policy=self.retry_policy,
            metadata={"endpoint": self.endpoint},
        )
        if not failure.retryable:
            raise VLMAdapterError(failure)


def build_ollama_generate_payload(
    *,
    model: str,
    prompt: str,
    image_bytes: bytes,
    temperature: float,
) -> dict[str, Any]:
    """Build an Ollama generate payload for one image."""

    image_base64 = base64.b64encode(image_bytes).decode("ascii")
    return {
        "model": model,
        "prompt": prompt,
        "images": [image_base64],
        "stream": False,
        "format": "json",
        "options": {"temperature": temperature},
    }


def _http_error_type(status_code: int) -> str:
    if status_code == 429:
        return "rate_limited"
    if status_code >= 500:
        return "server_error"
    return "http_error"


def extract_ollama_response_text(raw_text: str) -> str | None:
    """Extract Ollama's nested graph response text when present."""

    data = json.loads(raw_text)
    if not isinstance(data, Mapping):
        return None
    response = data.get("response")
    if isinstance(response, str):
        return response
    return None
