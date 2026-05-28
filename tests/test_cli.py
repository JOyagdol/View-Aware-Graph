import json
from pathlib import Path

import pytest
from PIL import Image
from typer.testing import CliRunner

from view_aware_graph.cli import app, extract_image_to_graph
from view_aware_graph.vlm import VLMRequest, VLMResponse, VLMSettings


class FakeAdapter:
    @property
    def provider(self) -> str:
        return "fake"

    @property
    def model(self) -> str:
        return "fake-model"

    def generate(self, request: VLMRequest) -> VLMResponse:
        graph = {
            "schema_version": "0.1.0",
            "source": {"image_id": request.image_id},
            "view": {
                "frame": "image",
                "coordinate_origin": "top_left",
                "bbox_format": "normalized_xywh",
                "assumptions": [],
            },
            "nodes": [],
            "edges": [],
        }
        raw_text = json.dumps({"response": json.dumps(graph), "done": True})
        return VLMResponse(
            provider=self.provider,
            model=self.model,
            raw_text=raw_text,
            graph_text=json.dumps(graph),
        )


def test_extract_image_to_graph_writes_raw_and_graph_outputs(tmp_path: Path) -> None:
    image_path = tmp_path / "input.jpg"
    Image.new("RGB", (100, 80), color=(240, 240, 240)).save(image_path)
    config_path = _write_config(tmp_path)
    output_path = tmp_path / "graph.json"

    result = extract_image_to_graph(
        image_path=image_path,
        config_path=config_path,
        output_path=output_path,
        run_id="unit_test",
        adapter=FakeAdapter(),
        verbose=False,
    )

    assert result.graph_output_path == output_path
    assert result.node_count == 0
    assert result.edge_count == 0
    assert result.repair_count == 0
    assert result.visualization_path == tmp_path / "graph.png"
    assert output_path.exists()
    assert (tmp_path / "graph.png").exists()
    assert (tmp_path / "interim" / "vlm_raw" / "unit_test_raw.json").exists()


def test_cli_extract_uses_create_adapter_monkeypatch(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    image_path = tmp_path / "input.jpg"
    Image.new("RGB", (100, 80), color=(240, 240, 240)).save(image_path)
    config_path = _write_config(tmp_path)
    output_path = tmp_path / "graph.json"

    monkeypatch.setenv("VLM_PROVIDER", "ollama")
    monkeypatch.setenv("VLM_MODEL", "qwen2.5vl:7b")

    def fake_create_adapter(_settings: VLMSettings) -> FakeAdapter:
        return FakeAdapter()

    monkeypatch.setattr("view_aware_graph.cli.create_adapter", fake_create_adapter)

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "extract",
            "--image",
            str(image_path),
            "--config",
            str(config_path),
            "--output",
            str(output_path),
            "--run-id",
            "cli_test",
        ],
    )

    assert result.exit_code == 0
    assert "graph_output=" in result.output
    assert "visualization=" in result.output
    assert "repairs=0" in result.output
    assert output_path.exists()
    assert (tmp_path / "graph.png").exists()


def test_cli_visualize_renders_existing_graph(tmp_path: Path) -> None:
    image_path = tmp_path / "input.jpg"
    Image.new("RGB", (100, 80), color=(240, 240, 240)).save(image_path)
    graph_path = tmp_path / "graph.json"
    output_path = tmp_path / "overlay.png"
    graph_path.write_text(
        json.dumps(
            {
                "nodes": [
                    {
                        "id": "monitor_right",
                        "label": "right monitor",
                        "type": "object",
                        "region": "center_right",
                    }
                ],
                "edges": [],
            }
        ),
        encoding="utf-8",
    )

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "visualize",
            "--graph",
            str(graph_path),
            "--image",
            str(image_path),
            "--output",
            str(output_path),
        ],
    )

    assert result.exit_code == 0
    assert f"visualization={output_path}" in result.output
    assert output_path.exists()


def _write_config(tmp_path: Path) -> Path:
    prompt_path = tmp_path / "prompt.md"
    prompt_path.write_text("Return JSON.", encoding="utf-8")
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        f"""
[project]
schema_version = "0.1.0"

[vlm]
provider = ""
model = ""
endpoint = "http://127.0.0.1:11434/api/generate"
temperature = 0.0
max_retries = 0
timeout_seconds = 600.0

[paths]
raw_data = "{tmp_path.as_posix()}/raw"
interim_data = "{tmp_path.as_posix()}/interim"
processed_data = "{tmp_path.as_posix()}/processed"
schema = "schemas/view_aware_graph.schema.json"
prompt = "{prompt_path.as_posix()}"
""".lstrip(),
        encoding="utf-8",
    )
    return config_path
