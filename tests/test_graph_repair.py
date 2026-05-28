from view_aware_graph.graph import repair_common_relation_drift


def test_repair_common_relation_drift_maps_partially_occluded_by() -> None:
    graph = {
        "edges": [
            {
                "id": "shelf_right_partially_occluded_by_monitor_right",
                "relation": "partially_occluded_by",
            }
        ]
    }

    repaired = repair_common_relation_drift(graph)

    assert repaired.repairs[0].path == "$.edges[0].relation"
    assert repaired.data["edges"][0]["id"] == "shelf_right_behind_monitor_right"
    assert repaired.data["edges"][0]["relation"] == "behind"
    assert repaired.data["edges"][0]["uncertainty"] == [
        "occluded",
        "viewpoint_inferred",
    ]


def test_repair_common_relation_drift_normalizes_object_global_observation() -> None:
    graph = {
        "global_observations": [
            {
                "description": "The screen content is ignored.",
                "uncertainty": ["screen_content"],
                "confidence": 0.8,
            }
        ]
    }

    repaired = repair_common_relation_drift(graph)

    assert repaired.data["global_observations"] == [
        "The screen content is ignored. (uncertainty=screen_content; confidence=0.8)"
    ]
    assert repaired.repairs[0].path == "$.global_observations[0]"


def test_repair_common_relation_drift_moves_region_bbox_to_bbox_2d() -> None:
    graph = {
        "nodes": [
            {
                "id": "monitor_right",
                "region": {"bbox_2d": [0.7, 0.1, 0.2, 0.8]},
            }
        ]
    }

    repaired = repair_common_relation_drift(graph)

    node = repaired.data["nodes"][0]
    assert node["bbox_2d"] == {
        "x": 0.7,
        "y": 0.1,
        "width": 0.2,
        "height": 0.8,
    }
    assert node["region"] == "right"
    assert repaired.repairs[0].path == "$.nodes[0].region"


def test_repair_common_relation_drift_normalizes_occlusion_list() -> None:
    graph = {
        "nodes": [
            {"id": "wall_center", "occlusion": ["monitor_right"]},
            {"id": "door_left", "occlusion": []},
        ]
    }

    repaired = repair_common_relation_drift(graph)

    assert repaired.data["nodes"][0]["occlusion"] == "partial"
    assert repaired.data["nodes"][0]["attributes"] == {
        "occluded_by": ["monitor_right"]
    }
    assert repaired.data["nodes"][0]["uncertainty"] == ["occluded"]
    assert repaired.data["nodes"][1]["occlusion"] == "none"
