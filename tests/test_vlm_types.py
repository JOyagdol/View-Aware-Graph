from pathlib import Path

from view_aware_graph.vlm import VLMRequest, VLMResponse


def test_vlm_request_carries_provider_neutral_fields() -> None:
    request = VLMRequest(
        image_path=Path("data/raw/example.jpg"),
        prompt="Return JSON.",
        image_id="example",
        metadata={"scene": "test"},
    )

    assert request.image_path == Path("data/raw/example.jpg")
    assert request.prompt == "Return JSON."
    assert request.image_id == "example"
    assert request.metadata["scene"] == "test"


def test_vlm_response_carries_raw_and_optional_graph_text() -> None:
    response = VLMResponse(
        provider="ollama",
        model="qwen2.5vl:7b",
        raw_text='{"response": "{}"}',
        graph_text="{}",
        metadata={"duration": 1.0},
    )

    assert response.provider == "ollama"
    assert response.model == "qwen2.5vl:7b"
    assert response.raw_text == '{"response": "{}"}'
    assert response.graph_text == "{}"
    assert response.metadata["duration"] == 1.0
