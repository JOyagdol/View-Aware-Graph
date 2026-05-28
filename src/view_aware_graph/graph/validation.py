"""Schema validation helpers for View-Aware Graph JSON."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

RELATION_REPAIR_SUGGESTIONS = {
    "partially_occluded_by": (
        "Use relation 'behind' and add uncertainty "
        "['occluded', 'viewpoint_inferred'] when image occlusion is intended."
    ),
}


@dataclass(frozen=True)
class ValidationIssue:
    """A readable schema validation issue."""

    path: str
    message: str
    validator: str
    value: Any
    suggestion: str | None = None


class GraphValidationError(ValueError):
    """Raised when graph JSON does not validate against the schema."""

    def __init__(self, issues: Sequence[ValidationIssue]) -> None:
        self.issues = list(issues)
        message = "\n".join(format_validation_issue(issue) for issue in self.issues)
        super().__init__(message)


def load_schema(schema_path: str | Path) -> dict[str, Any]:
    """Load a JSON schema from disk."""

    path = Path(schema_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Schema file did not contain a JSON object: {path}")
    return data


def validate_graph(graph: Mapping[str, Any], schema: Mapping[str, Any]) -> list[ValidationIssue]:
    """Return readable validation issues for a graph JSON object."""

    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(graph), key=lambda error: list(error.absolute_path))
    return [_issue_from_error(error) for error in errors]


def assert_valid_graph(graph: Mapping[str, Any], schema: Mapping[str, Any]) -> None:
    """Raise GraphValidationError if graph does not validate."""

    issues = validate_graph(graph, schema)
    if issues:
        raise GraphValidationError(issues)


def format_validation_issue(issue: ValidationIssue) -> str:
    """Format a validation issue for terminal output."""

    base = f"{issue.path}: {issue.message}"
    if issue.suggestion is None:
        return base
    return f"{base} Suggestion: {issue.suggestion}"


def _issue_from_error(error: Any) -> ValidationIssue:
    value = error.instance
    return ValidationIssue(
        path=_format_path(error.absolute_path),
        message=str(error.message),
        validator=str(error.validator),
        value=value,
        suggestion=_suggestion_for(error.validator, value, error.absolute_path),
    )


def _format_path(path_parts: Sequence[Any]) -> str:
    if not path_parts:
        return "$"

    path = "$"
    for part in path_parts:
        if isinstance(part, int):
            path += f"[{part}]"
        else:
            path += f".{part}"
    return path


def _suggestion_for(validator: str, value: Any, path_parts: Sequence[Any]) -> str | None:
    if validator != "enum" or not isinstance(value, str):
        return None

    if path_parts and path_parts[-1] == "relation":
        return RELATION_REPAIR_SUGGESTIONS.get(value)

    return None
