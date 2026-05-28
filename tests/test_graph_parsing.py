import json

import pytest

from view_aware_graph.graph import GraphParseError, parse_graph_json


def _minimal_graph() -> dict[str, object]:
    return {
        "schema_version": "0.1.0",
        "source": {"image_id": "test"},
        "view": {
            "frame": "image",
            "coordinate_origin": "top_left",
            "bbox_format": "normalized_xywh",
            "assumptions": [],
        },
        "nodes": [],
        "edges": [],
    }


def test_parse_direct_graph_json() -> None:
    graph = _minimal_graph()

    assert parse_graph_json(json.dumps(graph)) == graph


def test_parse_ollama_response_json() -> None:
    graph = _minimal_graph()
    response = {"model": "qwen2.5vl:7b", "response": json.dumps(graph), "done": True}

    assert parse_graph_json(json.dumps(response)) == graph


def test_parse_fenced_graph_json() -> None:
    graph = _minimal_graph()
    text = f"```json\n{json.dumps(graph)}\n```"

    assert parse_graph_json(text) == graph


def test_parse_invalid_response_raises_clear_error() -> None:
    with pytest.raises(GraphParseError, match="Invalid JSON"):
        parse_graph_json("{not json")
