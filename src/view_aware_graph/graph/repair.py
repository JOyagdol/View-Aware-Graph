"""Deterministic repair helpers for common VLM graph drift."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, TypeGuard


@dataclass(frozen=True)
class GraphRepair:
    """A deterministic graph repair record."""

    path: str
    before: Any
    after: Any
    note: str


@dataclass(frozen=True)
class RepairedGraph:
    """Graph data with repair records."""

    data: dict[str, Any]
    repairs: list[GraphRepair]


def repair_common_relation_drift(graph: dict[str, Any]) -> RepairedGraph:
    """Repair common VLM schema drift without changing the schema."""

    repaired = deepcopy(graph)
    repairs: list[GraphRepair] = []

    _repair_global_observations(repaired, repairs)
    _repair_node_field_drift(repaired, repairs)

    edges = repaired.get("edges")
    if not isinstance(edges, list):
        return RepairedGraph(data=repaired, repairs=repairs)

    for index, edge in enumerate(edges):
        if not isinstance(edge, dict):
            continue
        if edge.get("relation") == "partially_occluded_by":
            _repair_partially_occluded_by(edge)
            repairs.append(
                GraphRepair(
                    path=f"$.edges[{index}].relation",
                    before="partially_occluded_by",
                    after="behind",
                    note=(
                        "Mapped image occlusion wording to schema relation `behind` "
                        "with occlusion uncertainty."
                    ),
                )
            )

    return RepairedGraph(data=repaired, repairs=repairs)


def _repair_global_observations(graph: dict[str, Any], repairs: list[GraphRepair]) -> None:
    observations = graph.get("global_observations")
    if not isinstance(observations, list):
        return

    for index, observation in enumerate(observations):
        if not isinstance(observation, dict):
            continue
        description = observation.get("description")
        if not isinstance(description, str) or not description:
            continue
        details = []
        uncertainty = observation.get("uncertainty")
        if isinstance(uncertainty, list) and uncertainty:
            details.append(f"uncertainty={','.join(str(value) for value in uncertainty)}")
        confidence = observation.get("confidence")
        if isinstance(confidence, int | float):
            details.append(f"confidence={confidence:g}")
        after = description if not details else f"{description} ({'; '.join(details)})"
        observations[index] = after
        repairs.append(
            GraphRepair(
                path=f"$.global_observations[{index}]",
                before=observation,
                after=after,
                note="Converted object-style global observation to schema string.",
            )
        )


def _repair_node_field_drift(graph: dict[str, Any], repairs: list[GraphRepair]) -> None:
    nodes = graph.get("nodes")
    if not isinstance(nodes, list):
        return

    for index, node in enumerate(nodes):
        if not isinstance(node, dict):
            continue
        _repair_node_region(node, index, repairs)
        _repair_node_occlusion(node, index, repairs)


def _repair_node_region(
    node: dict[str, Any],
    index: int,
    repairs: list[GraphRepair],
) -> None:
    region = node.get("region")
    if not isinstance(region, dict):
        return
    bbox = region.get("bbox_2d")
    if not _is_bbox_list(bbox):
        return

    bbox_object = {
        "x": float(bbox[0]),
        "y": float(bbox[1]),
        "width": float(bbox[2]),
        "height": float(bbox[3]),
    }
    node["bbox_2d"] = bbox_object
    derived_region = _region_from_bbox(bbox_object)
    node["region"] = derived_region
    repairs.append(
        GraphRepair(
            path=f"$.nodes[{index}].region",
            before=region,
            after={"region": derived_region, "bbox_2d": bbox_object},
            note="Moved object-style region bbox into schema bbox_2d and derived coarse region.",
        )
    )


def _repair_node_occlusion(
    node: dict[str, Any],
    index: int,
    repairs: list[GraphRepair],
) -> None:
    occlusion = node.get("occlusion")
    if not isinstance(occlusion, list):
        return

    after = "partial" if occlusion else "none"
    node["occlusion"] = after
    if occlusion:
        attributes = node.get("attributes")
        if not isinstance(attributes, dict):
            attributes = {}
        attributes["occluded_by"] = [str(value) for value in occlusion]
        node["attributes"] = attributes
        uncertainty = node.get("uncertainty")
        if not isinstance(uncertainty, list):
            uncertainty = []
        if "occluded" not in uncertainty:
            uncertainty.append("occluded")
        node["uncertainty"] = uncertainty

    repairs.append(
        GraphRepair(
            path=f"$.nodes[{index}].occlusion",
            before=occlusion,
            after=after,
            note="Converted occluder-id list to schema occlusion level.",
        )
    )


def _repair_partially_occluded_by(edge: dict[str, Any]) -> None:
    edge["relation"] = "behind"
    edge["id"] = str(edge.get("id", "")).replace("partially_occluded_by", "behind")
    uncertainty = edge.get("uncertainty")
    if not isinstance(uncertainty, list):
        uncertainty = []
    for value in ("occluded", "viewpoint_inferred"):
        if value not in uncertainty:
            uncertainty.append(value)
    edge["uncertainty"] = uncertainty


def _is_bbox_list(value: Any) -> TypeGuard[list[int | float]]:
    if not isinstance(value, list) or len(value) != 4:
        return False
    return all(isinstance(item, int | float) for item in value)


def _region_from_bbox(bbox: dict[str, float]) -> str:
    center_x = bbox["x"] + bbox["width"] / 2
    center_y = bbox["y"] + bbox["height"] / 2
    if bbox["width"] >= 0.8 and bbox["height"] >= 0.8:
        return "full_frame"
    if bbox["width"] >= 0.75:
        if center_y < 0.33:
            return "top"
        if center_y > 0.67:
            return "bottom"
    if bbox["height"] >= 0.75:
        if center_x < 0.33:
            return "left"
        if center_x > 0.67:
            return "right"

    horizontal = _region_band(center_x, "left", "center", "right")
    vertical = _region_band(center_y, "upper", "center", "lower")
    if vertical == "center":
        return horizontal if horizontal != "center" else "center"
    if horizontal == "center":
        return f"{vertical}_center"
    return f"{vertical}_{horizontal}"


def _region_band(value: float, low: str, middle: str, high: str) -> str:
    if value < 0.33:
        return low
    if value > 0.67:
        return high
    return middle
