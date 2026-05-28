"""Provider-independent JSON extraction for VLM graph responses."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any, cast


class GraphParseError(ValueError):
    """Raised when a VLM response cannot be parsed as graph JSON."""


def parse_graph_json(response_text: str) -> dict[str, Any]:
    """Parse graph JSON from direct JSON, an Ollama response, or fenced text."""

    direct_error: GraphParseError | None = None
    try:
        parsed = _loads_json(response_text)
    except GraphParseError as exc:
        direct_error = exc
    else:
        if isinstance(parsed, Mapping):
            parsed_mapping = cast(Mapping[str, Any], parsed)
            if _looks_like_graph(parsed_mapping):
                return dict(parsed_mapping)

            response = parsed_mapping.get("response")
            if isinstance(response, str):
                nested = _loads_json(response)
                if isinstance(nested, Mapping):
                    return dict(cast(Mapping[str, Any], nested))
                raise GraphParseError("Ollama response field did not contain a JSON object.")

    extracted = _extract_first_json_object(response_text)
    if extracted is not None:
        parsed = _loads_json(extracted)
        if isinstance(parsed, Mapping):
            return dict(cast(Mapping[str, Any], parsed))

    if direct_error is not None:
        raise direct_error

    raise GraphParseError("Could not parse a View-Aware Graph JSON object from response.")


def _loads_json(text: str) -> Any:
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        message = f"Invalid JSON: {exc.msg} at line {exc.lineno}, column {exc.colno}."
        raise GraphParseError(message) from exc


def _looks_like_graph(value: Mapping[str, Any]) -> bool:
    required_keys = {"schema_version", "source", "view", "nodes", "edges"}
    return required_keys.issubset(value.keys())


def _extract_first_json_object(text: str) -> str | None:
    start = text.find("{")
    if start == -1:
        return None

    depth = 0
    in_string = False
    escaped = False

    for index, char in enumerate(text[start:], start=start):
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]

    return None
