import base64
import json
from pathlib import Path

import pytest

from view_aware_graph.vlm import (
    OllamaAdapter,
    RetryPolicy,
    VLMAdapterError,
    VLMRequest,
    build_ollama_generate_payload,
    extract_ollama_response_text,
)


def test_build_ollama_generate_payload_encodes_image() -> None:
    payload = build_ollama_generate_payload(
        model="qwen2.5vl:7b",
        prompt="Return JSON.",
        image_bytes=b"image-bytes",
        temperature=0.0,
    )

    assert payload["model"] == "qwen2.5vl:7b"
    assert payload["prompt"] == "Return JSON."
    assert payload["images"] == [base64.b64encode(b"image-bytes").decode("ascii")]
    assert payload["stream"] is False
    assert payload["format"] == "json"
    assert payload["options"] == {"temperature": 0.0}


def test_extract_ollama_response_text_returns_nested_response() -> None:
    raw_text = json.dumps({"response": '{"schema_version": "0.1.0"}', "done": True})

    assert extract_ollama_response_text(raw_text) == '{"schema_version": "0.1.0"}'


def test_ollama_adapter_generate_uses_injected_transport(tmp_path: Path) -> None:
    image_path = tmp_path / "image.jpg"
    image_path.write_bytes(b"image-bytes")
    captured_payloads: list[dict[str, object]] = []

    def transport(payload: bytes) -> bytes:
        captured_payloads.append(json.loads(payload.decode("utf-8")))
        return json.dumps({"response": '{"schema_version": "0.1.0"}'}).encode("utf-8")

    adapter = OllamaAdapter(
        model="qwen2.5vl:7b",
        endpoint="http://127.0.0.1:11434/api/generate",
        retry_policy=RetryPolicy(max_retries=0),
        transport=transport,
    )
    response = adapter.generate(
        VLMRequest(image_path=image_path, prompt="Return JSON.", image_id="test")
    )

    assert response.provider == "ollama"
    assert response.model == "qwen2.5vl:7b"
    assert response.graph_text == '{"schema_version": "0.1.0"}'
    assert response.metadata["attempts"] == 1
    assert captured_payloads[0]["model"] == "qwen2.5vl:7b"


def test_ollama_adapter_retries_retryable_transport_error(tmp_path: Path) -> None:
    image_path = tmp_path / "image.jpg"
    image_path.write_bytes(b"image-bytes")
    attempts = 0

    def transport(_payload: bytes) -> bytes:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise TimeoutError("slow response")
        return json.dumps({"response": "{}"}).encode("utf-8")

    adapter = OllamaAdapter(
        model="qwen2.5vl:7b",
        endpoint="http://127.0.0.1:11434/api/generate",
        retry_policy=RetryPolicy(max_retries=1),
        transport=transport,
    )
    response = adapter.generate(
        VLMRequest(image_path=image_path, prompt="Return JSON.", image_id="test")
    )

    assert attempts == 2
    assert response.graph_text == "{}"


def test_ollama_adapter_raises_structured_failure_after_retries(tmp_path: Path) -> None:
    image_path = tmp_path / "image.jpg"
    image_path.write_bytes(b"image-bytes")

    def transport(_payload: bytes) -> bytes:
        raise TimeoutError("slow response")

    adapter = OllamaAdapter(
        model="qwen2.5vl:7b",
        endpoint="http://127.0.0.1:11434/api/generate",
        retry_policy=RetryPolicy(max_retries=1),
        transport=transport,
    )

    with pytest.raises(VLMAdapterError) as exc_info:
        adapter.generate(
            VLMRequest(image_path=image_path, prompt="Return JSON.", image_id="test")
        )

    assert exc_info.value.failure.error_type == "timeout"
    assert exc_info.value.failure.attempts == 2
    assert exc_info.value.failure.retryable is False
