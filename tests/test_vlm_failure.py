from pathlib import Path

from view_aware_graph.vlm import (
    RetryPolicy,
    VLMAdapterError,
    VLMRequest,
    build_failure_report,
)


def _request() -> VLMRequest:
    return VLMRequest(
        image_path=Path("data/raw/example.jpg"),
        prompt="Return JSON.",
        image_id="example",
    )


def test_retry_policy_counts_initial_attempt() -> None:
    policy = RetryPolicy(max_retries=2)

    assert policy.max_attempts == 3


def test_failure_report_marks_retryable_error_before_attempt_limit() -> None:
    failure = build_failure_report(
        provider="ollama",
        model="qwen2.5vl:7b",
        request=_request(),
        error_type="timeout",
        message="request timed out",
        attempts=1,
        retry_policy=RetryPolicy(max_retries=2),
    )

    assert failure.image_id == "example"
    assert failure.retryable is True


def test_failure_report_marks_non_retryable_error() -> None:
    failure = build_failure_report(
        provider="ollama",
        model="qwen2.5vl:7b",
        request=_request(),
        error_type="schema_mismatch",
        message="invalid relation",
        attempts=1,
        retry_policy=RetryPolicy(max_retries=2),
    )

    assert failure.retryable is False


def test_failure_report_marks_attempt_limit_exhausted() -> None:
    failure = build_failure_report(
        provider="ollama",
        model="qwen2.5vl:7b",
        request=_request(),
        error_type="timeout",
        message="request timed out",
        attempts=3,
        retry_policy=RetryPolicy(max_retries=2),
    )

    assert failure.retryable is False


def test_adapter_error_carries_failure_report() -> None:
    failure = build_failure_report(
        provider="ollama",
        model="qwen2.5vl:7b",
        request=_request(),
        error_type="connection_error",
        message="ollama unavailable",
        attempts=1,
        retry_policy=RetryPolicy(max_retries=2),
        raw_response_path=Path("data/interim/vlm_raw/example_raw.json"),
    )

    error = VLMAdapterError(failure)

    assert str(error) == "ollama unavailable"
    assert error.failure.raw_response_path == Path(
        "data/interim/vlm_raw/example_raw.json"
    )
