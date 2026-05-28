"""Provider-neutral VLM request and response contracts."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class RetryPolicy:
    """Provider-neutral retry settings for VLM calls."""

    max_retries: int
    retryable_error_types: tuple[str, ...] = (
        "timeout",
        "connection_error",
        "rate_limited",
        "server_error",
    )

    @property
    def max_attempts(self) -> int:
        """Total attempts including the initial call."""

        return self.max_retries + 1


@dataclass(frozen=True)
class VLMRequest:
    """A provider-neutral image-to-graph VLM request."""

    image_path: Path
    prompt: str
    image_id: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class VLMResponse:
    """A provider-neutral VLM response before graph parsing and validation."""

    provider: str
    model: str
    raw_text: str
    graph_text: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class VLMFailure:
    """Structured failure report for a VLM request."""

    provider: str
    model: str
    image_id: str
    error_type: str
    message: str
    attempts: int
    retryable: bool
    raw_response_path: Path | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


class VLMAdapterError(RuntimeError):
    """Raised when a VLM adapter cannot complete a request."""

    def __init__(self, failure: VLMFailure) -> None:
        self.failure = failure
        super().__init__(failure.message)


def build_failure_report(
    *,
    provider: str,
    model: str,
    request: VLMRequest,
    error_type: str,
    message: str,
    attempts: int,
    retry_policy: RetryPolicy,
    raw_response_path: Path | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> VLMFailure:
    """Build a structured failure report with retryability attached."""

    return VLMFailure(
        provider=provider,
        model=model,
        image_id=request.image_id,
        error_type=error_type,
        message=message,
        attempts=attempts,
        retryable=_is_retryable(error_type, attempts, retry_policy),
        raw_response_path=raw_response_path,
        metadata={} if metadata is None else metadata,
    )


def _is_retryable(error_type: str, attempts: int, retry_policy: RetryPolicy) -> bool:
    return error_type in retry_policy.retryable_error_types and attempts < retry_policy.max_attempts
