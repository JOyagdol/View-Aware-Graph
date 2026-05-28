from pathlib import Path
from typing import Any

from PIL import Image

from view_aware_graph.graph import (
    default_visualization_path,
    render_graph_png,
    render_graph_svg,
    render_graph_visualization,
)


def test_default_visualization_path_uses_png_suffix() -> None:
    assert default_visualization_path(Path("data/processed/view_graphs/run.json")) == Path(
        "data/processed/view_graphs/run.png"
    )


def test_render_graph_svg_writes_overlay(tmp_path: Path) -> None:
    image_path = _write_image(tmp_path)
    output_path = tmp_path / "graph.svg"

    render_graph_svg(graph=_graph(), image_path=image_path, output_path=output_path)

    text = output_path.read_text(encoding="utf-8")
    assert "<svg" in text
    assert "<circle" in text
    assert "right monitor 0.82" in text
    assert "central wall" in text
    assert "in_front_of" in text


def test_render_graph_png_writes_overlay(tmp_path: Path) -> None:
    image_path = _write_image(tmp_path)
    output_path = tmp_path / "graph.png"

    render_graph_png(graph=_graph(), image_path=image_path, output_path=output_path)

    assert output_path.exists()
    with Image.open(output_path) as image:
        assert image.format == "PNG"
        assert image.size == (100, 80)


def test_render_graph_visualization_uses_suffix(tmp_path: Path) -> None:
    image_path = _write_image(tmp_path)
    output_path = tmp_path / "graph.png"

    render_graph_visualization(graph=_graph(), image_path=image_path, output_path=output_path)

    with Image.open(output_path) as image:
        assert image.format == "PNG"


def _write_image(tmp_path: Path) -> Path:
    image_path = tmp_path / "image.png"
    Image.new("RGB", (100, 80), color=(240, 240, 240)).save(image_path)
    return image_path


def _graph() -> dict[str, Any]:
    return {
        "nodes": [
            {
                "id": "monitor_right",
                "label": "right monitor",
                "type": "object",
                "bbox_2d": {"x": 0.7, "y": 0.1, "width": 0.2, "height": 0.4},
                "confidence": 0.82,
            },
            {
                "id": "wall_center",
                "label": "central wall",
                "type": "wall",
                "region": "center",
            },
        ],
        "edges": [
            {
                "source": "monitor_right",
                "target": "wall_center",
                "relation": "in_front_of",
            }
        ],
    }
