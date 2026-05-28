"""Visualization helpers for View-Aware Graph outputs."""

from __future__ import annotations

import math
import os
from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Any, TypeAlias

from PIL import Image, ImageDraw, ImageFont

PngFont: TypeAlias = ImageFont.ImageFont | ImageFont.FreeTypeFont

EDGE_WIDTH = 10
TEXT_PADDING = 8
TEXT_OUTLINE_WIDTH = 4

REGION_BOXES: dict[str, tuple[float, float, float, float]] = {
    "upper_left": (0.0, 0.0, 1 / 3, 1 / 3),
    "upper_center": (1 / 3, 0.0, 1 / 3, 1 / 3),
    "upper_right": (2 / 3, 0.0, 1 / 3, 1 / 3),
    "center_left": (0.0, 1 / 3, 1 / 3, 1 / 3),
    "center": (1 / 3, 1 / 3, 1 / 3, 1 / 3),
    "center_right": (2 / 3, 1 / 3, 1 / 3, 1 / 3),
    "lower_left": (0.0, 2 / 3, 1 / 3, 1 / 3),
    "lower_center": (1 / 3, 2 / 3, 1 / 3, 1 / 3),
    "lower_right": (2 / 3, 2 / 3, 1 / 3, 1 / 3),
    "left": (0.0, 0.0, 0.35, 1.0),
    "right": (0.65, 0.0, 0.35, 1.0),
    "top": (0.0, 0.0, 1.0, 0.35),
    "bottom": (0.0, 0.65, 1.0, 0.35),
    "full_frame": (0.0, 0.0, 1.0, 1.0),
}

NODE_COLORS: dict[str, str] = {
    "wall": "#2563eb",
    "door": "#16a34a",
    "window": "#0891b2",
    "opening": "#0d9488",
    "floor": "#ca8a04",
    "ceiling": "#9333ea",
    "surface": "#64748b",
    "panel": "#c2410c",
    "furniture": "#db2777",
    "object": "#dc2626",
    "unknown": "#525252",
}


@dataclass(frozen=True)
class NodeLayout:
    """Computed drawing box for a graph node."""

    node: dict[str, Any]
    x: float
    y: float
    width: float
    height: float
    center_x: float
    center_y: float


def render_graph_visualization(
    *,
    graph: dict[str, Any],
    image_path: Path,
    output_path: Path,
) -> None:
    """Render a graph overlay as PNG by default, or SVG when requested by suffix."""

    if output_path.suffix.lower() == ".svg":
        render_graph_svg(graph=graph, image_path=image_path, output_path=output_path)
        return
    render_graph_png(graph=graph, image_path=image_path, output_path=output_path)


def render_graph_png(
    *,
    graph: dict[str, Any],
    image_path: Path,
    output_path: Path,
) -> None:
    """Render a raster PNG graph overlay next to local graph outputs."""

    with Image.open(image_path) as source_image:
        image = source_image.convert("RGBA")
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 16))
    draw = ImageDraw.Draw(overlay)
    font = _load_font(image.width)
    nodes = _node_layouts(graph, image.width, image.height)

    _draw_png_edges(draw, graph, nodes, font)
    _draw_png_nodes(draw, nodes, font)

    output = Image.alpha_composite(image, overlay).convert("RGB")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output.save(output_path, format="PNG")


def render_graph_svg(
    *,
    graph: dict[str, Any],
    image_path: Path,
    output_path: Path,
) -> None:
    """Render a lightweight graph overlay SVG next to local graph outputs."""

    width, height = _image_size(image_path)
    image_href = _image_href(image_path, output_path)
    nodes = _node_layouts(graph, width, height)

    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}">'
        ),
        "<defs>",
        (
            '<marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" '
            'markerWidth="8" markerHeight="8" orient="auto-start-reverse">'
            '<path d="M 0 0 L 10 5 L 0 10 z" fill="#111827" /></marker>'
        ),
        "</defs>",
        f'<image href="{escape(image_href)}" x="0" y="0" width="{width}" height="{height}" />',
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="#000000" opacity="0.06" />',
    ]

    parts.extend(_edge_svg(graph, nodes))
    parts.extend(_node_svg(nodes))
    parts.append("</svg>")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(parts) + "\n", encoding="utf-8")


def default_visualization_path(graph_output_path: Path) -> Path:
    """Return the default PNG path for a graph JSON output path."""

    return graph_output_path.with_suffix(".png")


def _node_layouts(
    graph: dict[str, Any],
    image_width: int,
    image_height: int,
) -> dict[str, NodeLayout]:
    nodes = graph.get("nodes")
    if not isinstance(nodes, list):
        return {}

    layouts: dict[str, NodeLayout] = {}
    for index, node in enumerate(nodes):
        if not isinstance(node, dict):
            continue
        node_id = node.get("id")
        if not isinstance(node_id, str) or not node_id:
            continue
        box = _node_box(node)
        if box is None:
            box = _fallback_box(index)
        x, y, width, height = _scale_box(box, image_width, image_height)
        layouts[node_id] = NodeLayout(
            node=node,
            x=x,
            y=y,
            width=width,
            height=height,
            center_x=x + width / 2,
            center_y=y + height / 2,
        )
    return layouts


def _node_box(node: dict[str, Any]) -> tuple[float, float, float, float] | None:
    bbox = node.get("bbox_2d")
    if isinstance(bbox, dict):
        x = _number(bbox.get("x"))
        y = _number(bbox.get("y"))
        width = _number(bbox.get("width"))
        height = _number(bbox.get("height"))
        if x is not None and y is not None and width is not None and height is not None:
            return (x, y, width, height)

    region = node.get("region")
    if isinstance(region, str):
        return REGION_BOXES.get(region)
    return None


def _edge_svg(graph: dict[str, Any], nodes: dict[str, NodeLayout]) -> list[str]:
    edges = graph.get("edges")
    if not isinstance(edges, list):
        return []

    parts: list[str] = ['<g id="edges" stroke="#111827" stroke-width="3" opacity="0.82">']
    for edge in edges:
        if not isinstance(edge, dict):
            continue
        source = edge.get("source")
        target = edge.get("target")
        if not isinstance(source, str) or not isinstance(target, str):
            continue
        source_node = nodes.get(source)
        target_node = nodes.get(target)
        if source_node is None or target_node is None:
            continue
        relation = edge.get("relation")
        label = relation if isinstance(relation, str) else "unknown"
        x1 = source_node.center_x
        y1 = source_node.center_y
        x2 = target_node.center_x
        y2 = target_node.center_y
        label_x = (x1 + x2) / 2
        label_y = (y1 + y2) / 2
        parts.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            'marker-end="url(#arrow)" />'
        )
        parts.append(
            f'<text x="{label_x:.1f}" y="{label_y:.1f}" font-size="18" '
            'font-family="Arial, sans-serif" fill="#111827" stroke="#ffffff" '
            f'stroke-width="4" paint-order="stroke">{escape(label)}</text>'
        )
    parts.append("</g>")
    return parts


def _node_svg(nodes: dict[str, NodeLayout]) -> list[str]:
    parts: list[str] = []
    for node_id, layout in nodes.items():
        node = layout.node
        node_type = node.get("type")
        color = NODE_COLORS.get(node_type if isinstance(node_type, str) else "unknown", "#525252")
        label = node.get("label")
        display_label = label if isinstance(label, str) and label else node_id
        confidence = node.get("confidence")
        if isinstance(confidence, int | float):
            display_label = f"{display_label} {confidence:.2f}"
        text_x = layout.center_x + 10
        text_y = max(20.0, layout.center_y - 10)
        parts.append(
            f'<g id="node-{escape(node_id)}">'
            f'<circle cx="{layout.center_x:.1f}" cy="{layout.center_y:.1f}" r="8" '
            f'fill="{color}" stroke="#ffffff" stroke-width="3" />'
            f'<text x="{text_x:.1f}" y="{text_y:.1f}" font-size="20" '
            'font-family="Arial, sans-serif" font-weight="700" '
            f'fill="{color}" stroke="#ffffff" stroke-width="5" paint-order="stroke">'
            f'{escape(display_label)}</text></g>'
        )
    return parts


def _draw_png_edges(
    draw: ImageDraw.ImageDraw,
    graph: dict[str, Any],
    nodes: dict[str, NodeLayout],
    font: PngFont,
) -> None:
    edges = graph.get("edges")
    if not isinstance(edges, list):
        return

    for edge in edges:
        if not isinstance(edge, dict):
            continue
        source = edge.get("source")
        target = edge.get("target")
        if not isinstance(source, str) or not isinstance(target, str):
            continue
        source_node = nodes.get(source)
        target_node = nodes.get(target)
        if source_node is None or target_node is None:
            continue
        start = (source_node.center_x, source_node.center_y)
        end = (target_node.center_x, target_node.center_y)
        draw.line([start, end], fill=(17, 24, 39, 245), width=EDGE_WIDTH)
        _draw_arrowhead(draw, start, end)
        relation = edge.get("relation")
        if isinstance(relation, str):
            label_position = (
                (source_node.center_x + target_node.center_x) / 2,
                (source_node.center_y + target_node.center_y) / 2,
            )
            _draw_text_with_outline(
                draw,
                label_position,
                relation,
                fill=(17, 24, 39, 255),
                font=font,
            )


def _draw_png_nodes(
    draw: ImageDraw.ImageDraw,
    nodes: dict[str, NodeLayout],
    font: PngFont,
) -> None:
    for node_id, layout in nodes.items():
        node = layout.node
        node_type = node.get("type")
        color_hex = NODE_COLORS.get(
            node_type if isinstance(node_type, str) else "unknown",
            "#525252",
        )
        color = _hex_to_rgb(color_hex)
        radius = max(18, min(34, int(layout.width / 9)))
        point_box = [
            layout.center_x - radius,
            layout.center_y - radius,
            layout.center_x + radius,
            layout.center_y + radius,
        ]
        draw.ellipse(point_box, fill=(*color, 255), outline=(255, 255, 255, 255), width=6)
        label = node.get("label")
        display_label = label if isinstance(label, str) and label else node_id
        confidence = node.get("confidence")
        if isinstance(confidence, int | float):
            display_label = f"{display_label} {confidence:.2f}"
        text_position = (
            layout.center_x + radius + 10,
            max(8.0, layout.center_y - _font_size(font) - 8),
        )
        _draw_text_with_outline(
            draw,
            text_position,
            display_label,
            fill=(*color, 255),
            font=font,
        )


def _draw_text_with_outline(
    draw: ImageDraw.ImageDraw,
    position: tuple[float, float],
    text: str,
    *,
    fill: tuple[int, int, int, int],
    font: PngFont,
) -> None:
    x, y = position
    bbox = draw.textbbox((x, y), text, font=font)
    background = (
        bbox[0] - TEXT_PADDING,
        bbox[1] - TEXT_PADDING,
        bbox[2] + TEXT_PADDING,
        bbox[3] + TEXT_PADDING,
    )
    draw.rounded_rectangle(background, radius=8, fill=(255, 255, 255, 220))
    offsets = [
        (-TEXT_OUTLINE_WIDTH, 0),
        (TEXT_OUTLINE_WIDTH, 0),
        (0, -TEXT_OUTLINE_WIDTH),
        (0, TEXT_OUTLINE_WIDTH),
    ]
    for offset_x, offset_y in offsets:
        draw.text((x + offset_x, y + offset_y), text, fill=(255, 255, 255, 245), font=font)
    draw.text((x, y), text, fill=fill, font=font)


def _draw_arrowhead(
    draw: ImageDraw.ImageDraw,
    start: tuple[float, float],
    end: tuple[float, float],
) -> None:
    start_x, start_y = start
    end_x, end_y = end
    angle = math.atan2(end_y - start_y, end_x - start_x)
    length = 30
    spread = 0.55
    points = [end]
    for delta in (math.pi - spread, math.pi + spread):
        points.append(
            (
                end_x + math.cos(angle + delta) * length,
                end_y + math.sin(angle + delta) * length,
            )
        )
    draw.polygon(points, fill=(17, 24, 39, 230))


def _hex_to_rgb(value: str) -> tuple[int, int, int]:
    stripped = value.lstrip("#")
    return (
        int(stripped[0:2], 16),
        int(stripped[2:4], 16),
        int(stripped[4:6], 16),
    )


def _load_font(image_width: int) -> PngFont:
    size = max(28, min(64, image_width // 38))
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf", size=size)
    except OSError:
        return ImageFont.load_default()


def _font_size(font: PngFont) -> int:
    bbox = font.getbbox("Ag")
    return int(bbox[3] - bbox[1])


def _scale_box(
    box: tuple[float, float, float, float],
    image_width: int,
    image_height: int,
) -> tuple[float, float, float, float]:
    x, y, width, height = box
    return (
        x * image_width,
        y * image_height,
        max(width * image_width, 12.0),
        max(height * image_height, 12.0),
    )


def _fallback_box(index: int) -> tuple[float, float, float, float]:
    column = index % 4
    row = index // 4
    return (0.02 + column * 0.24, 0.02 + row * 0.12, 0.2, 0.08)


def _image_href(image_path: Path, output_path: Path) -> str:
    try:
        return os.path.relpath(image_path, output_path.parent)
    except ValueError:
        return image_path.as_posix()


def _image_size(image_path: Path) -> tuple[int, int]:
    with image_path.open("rb") as handle:
        header = handle.read(32)
        if header.startswith(b"\x89PNG\r\n\x1a\n"):
            width = int.from_bytes(header[16:20], "big")
            height = int.from_bytes(header[20:24], "big")
            return width, height
        if header.startswith(b"\xff\xd8"):
            return _jpeg_size(image_path)
    return (1000, 1000)


def _jpeg_size(image_path: Path) -> tuple[int, int]:
    with image_path.open("rb") as handle:
        handle.read(2)
        while True:
            marker_start = handle.read(1)
            if marker_start != b"\xff":
                raise ValueError(f"Cannot read JPEG size from {image_path}")
            marker = handle.read(1)
            while marker == b"\xff":
                marker = handle.read(1)
            if marker in {b"\xc0", b"\xc1", b"\xc2", b"\xc3"}:
                handle.read(3)
                height = int.from_bytes(handle.read(2), "big")
                width = int.from_bytes(handle.read(2), "big")
                return width, height
            segment_length = int.from_bytes(handle.read(2), "big")
            handle.seek(segment_length - 2, os.SEEK_CUR)


def _number(value: Any) -> float | None:
    if isinstance(value, int | float):
        return float(value)
    return None
