from view_aware_graph.graph import assert_valid_graph, validate_graph


def _schema() -> dict[str, object]:
    return {
        "type": "object",
        "required": ["edges"],
        "properties": {
            "edges": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["relation"],
                    "properties": {
                        "relation": {
                            "type": "string",
                            "enum": ["behind", "in_front_of", "supports"],
                        }
                    },
                },
            }
        },
    }


def test_validate_graph_returns_no_issues_for_valid_graph() -> None:
    graph = {"edges": [{"relation": "behind"}]}

    assert validate_graph(graph, _schema()) == []
    assert_valid_graph(graph, _schema())


def test_validate_graph_suggests_common_relation_repair() -> None:
    graph = {"edges": [{"relation": "partially_occluded_by"}]}

    issues = validate_graph(graph, _schema())

    assert len(issues) == 1
    assert issues[0].path == "$.edges[0].relation"
    assert issues[0].validator == "enum"
    assert issues[0].value == "partially_occluded_by"
    assert issues[0].suggestion is not None
    assert "behind" in issues[0].suggestion
