"""Command-line workflow for View-Aware Graph extraction."""

from __future__ import annotations

import json
import sys
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass
from itertools import cycle
from pathlib import Path
from threading import Event, Thread
from time import perf_counter
from typing import Annotated, Any

import typer

from view_aware_graph.graph import (
    default_visualization_path,
    format_validation_issue,
    load_schema,
    parse_graph_json,
    render_graph_visualization,
    repair_common_relation_drift,
    validate_graph,
)
from view_aware_graph.vlm import (
    OllamaAdapter,
    VLMAdapter,
    VLMAdapterError,
    VLMRequest,
    VLMSettings,
    graph_output_path,
    load_vlm_settings,
    raw_response_path,
)

app = typer.Typer(no_args_is_help=True)


@app.callback()
def main() -> None:
    """View-Aware Graph command-line tools."""


@dataclass(frozen=True)
class ExtractionResult:
    """Result summary for one image-to-graph extraction run."""

    raw_response_path: Path
    graph_output_path: Path
    node_count: int
    edge_count: int
    repair_count: int
    visualization_path: Path | None = None


def extract_image_to_graph(
    *,
    image_path: Path,
    config_path: Path,
    output_path: Path | None = None,
    run_id: str | None = None,
    adapter: VLMAdapter | None = None,
    repair_common_relations: bool = True,
    visualization_path: Path | None = None,
    write_visualization: bool = True,
    verbose: bool = False,
) -> ExtractionResult:
    """Run VLM extraction, validate the graph JSON, and write local outputs."""

    total_start = perf_counter()

    settings_start = _log_start(verbose, "Loading settings")
    settings = load_vlm_settings(config_path)
    _log_done(verbose, "Loaded settings", settings_start)
    resolved_run_id = run_id or image_path.stem
    resolved_output_path = output_path or graph_output_path(settings, resolved_run_id)
    resolved_raw_path = raw_response_path(settings, resolved_run_id)
    resolved_visualization_path = (
        visualization_path or default_visualization_path(resolved_output_path)
        if write_visualization
        else None
    )

    prompt_start = _log_start(verbose, f"Reading prompt: {settings.prompt_path}")
    prompt = _prompt_for_image(settings.prompt_path, image_path, resolved_run_id)
    _log_done(verbose, f"Read prompt ({len(prompt)} chars)", prompt_start)

    vlm_adapter = adapter or create_adapter(settings)
    image_size = _file_size(image_path)
    request_message = (
        f"Sending image to {vlm_adapter.provider}:{vlm_adapter.model} ({image_size} bytes)"
    )
    with _spinner(verbose, request_message):
        try:
            response = vlm_adapter.generate(
                VLMRequest(image_path=image_path, prompt=prompt, image_id=resolved_run_id)
            )
        except VLMAdapterError as exc:
            raise typer.BadParameter(_format_vlm_adapter_error(exc, settings)) from exc

    raw_start = _log_start(verbose, f"Writing raw response: {resolved_raw_path}")
    _write_text(resolved_raw_path, response.raw_text)
    _log_done(verbose, f"Wrote raw response ({_file_size(resolved_raw_path)} bytes)", raw_start)

    parse_start = _log_start(verbose, "Parsing graph JSON")
    graph = parse_graph_json(response.graph_text or response.raw_text)
    _log_done(verbose, "Parsed graph JSON", parse_start)

    validation_start = _log_start(verbose, f"Validating graph JSON: {settings.schema_path}")
    schema = load_schema(settings.schema_path)
    issues = validate_graph(graph, schema)
    repair_count = 0
    if issues and repair_common_relations:
        repair_start = _log_start(verbose, "Trying deterministic common-relation repair")
        repaired = repair_common_relation_drift(graph)
        if repaired.repairs:
            graph = repaired.data
            repair_count = len(repaired.repairs)
            issues = validate_graph(graph, schema)
        _log_done(verbose, f"Repair attempt finished ({repair_count} repairs)", repair_start)

    if issues:
        issue_text = "\n".join(format_validation_issue(issue) for issue in issues)
        raise typer.BadParameter(f"Graph JSON failed schema validation:\n{issue_text}")
    _log_done(verbose, "Validated graph JSON", validation_start)

    output_start = _log_start(verbose, f"Writing graph output: {resolved_output_path}")
    _write_json(resolved_output_path, graph)
    output_size = _file_size(resolved_output_path)
    _log_done(verbose, f"Wrote graph output ({output_size} bytes)", output_start)

    if resolved_visualization_path is not None:
        visualization_start = _log_start(
            verbose,
            f"Writing graph visualization: {resolved_visualization_path}",
        )
        render_graph_visualization(
            graph=graph,
            image_path=image_path,
            output_path=resolved_visualization_path,
        )
        _log_done(
            verbose,
            f"Wrote graph visualization ({_file_size(resolved_visualization_path)} bytes)",
            visualization_start,
        )
    _log_done(verbose, "Completed extraction", total_start)

    return ExtractionResult(
        raw_response_path=resolved_raw_path,
        graph_output_path=resolved_output_path,
        node_count=_item_count(graph, "nodes"),
        edge_count=_item_count(graph, "edges"),
        repair_count=repair_count,
        visualization_path=resolved_visualization_path,
    )


def create_adapter(settings: VLMSettings) -> VLMAdapter:
    """Create a concrete adapter from provider settings."""

    if settings.provider != "ollama":
        raise typer.BadParameter("Only provider 'ollama' is supported by the current CLI.")
    if not settings.model:
        raise typer.BadParameter("A VLM model is required. Set VLM_MODEL or configs/default.toml.")

    return OllamaAdapter(
        model=settings.model,
        endpoint=settings.endpoint,
        temperature=settings.temperature,
        retry_policy=settings.retry_policy,
        timeout_seconds=settings.timeout_seconds,
    )


@app.command()
def extract(
    image: Annotated[
        Path,
        typer.Option(
            "--image",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            help="Input image path.",
        ),
    ],
    config: Annotated[
        Path,
        typer.Option("--config", help="TOML config path."),
    ] = Path("configs/default.toml"),
    output: Annotated[
        Path | None,
        typer.Option("--output", help="Output graph JSON path."),
    ] = None,
    run_id: Annotated[
        str | None,
        typer.Option("--run-id", help="Run id used for default output names."),
    ] = None,
    repair_common_relations: Annotated[
        bool,
        typer.Option(
            "--repair-common-relations/--no-repair-common-relations",
            help="Apply deterministic repairs for known schema vocabulary drift.",
        ),
    ] = True,
    visualization: Annotated[
        Path | None,
        typer.Option(
            "--visualization",
            help="Write a graph overlay to this path. Defaults to <output>.png.",
        ),
    ] = None,
    no_visualization: Annotated[
        bool,
        typer.Option(
            "--no-visualization",
            help="Disable visualization output.",
        ),
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Print progress logs."),
    ] = True,
) -> None:
    """Extract a View-Aware Graph JSON from one image."""

    result = extract_image_to_graph(
        image_path=image,
        config_path=config,
        output_path=output,
        run_id=run_id,
        repair_common_relations=repair_common_relations,
        visualization_path=visualization,
        write_visualization=not no_visualization,
        verbose=verbose,
    )
    typer.echo(f"raw_response={result.raw_response_path}")
    typer.echo(f"graph_output={result.graph_output_path}")
    if result.visualization_path is not None:
        typer.echo(f"visualization={result.visualization_path}")
    typer.echo(f"nodes={result.node_count}")
    typer.echo(f"edges={result.edge_count}")
    typer.echo(f"repairs={result.repair_count}")


@app.command()
def visualize(
    graph: Annotated[
        Path,
        typer.Option(
            "--graph",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            help="Existing graph JSON path.",
        ),
    ],
    image: Annotated[
        Path,
        typer.Option(
            "--image",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            help="Input image path used as visualization background.",
        ),
    ],
    output: Annotated[
        Path | None,
        typer.Option("--output", help="Output overlay path. Defaults to <graph>.png."),
    ] = None,
) -> None:
    """Render a graph overlay from an existing graph JSON without calling a VLM."""

    graph_data = _read_json(graph)
    output_path = output or default_visualization_path(graph)
    render_graph_visualization(graph=graph_data, image_path=image, output_path=output_path)
    typer.echo(f"visualization={output_path}")


def _prompt_for_image(prompt_path: Path, image_path: Path, image_id: str) -> str:
    prompt = prompt_path.read_text(encoding="utf-8")
    return (
        f"{prompt}\n\n"
        f"For this run, set source.image_id to {image_id} "
        f"and source.image_path to {image_path.as_posix()}."
    )


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, data: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise typer.BadParameter("Graph JSON must be a JSON object.")
    return data


def _item_count(data: Mapping[str, Any], key: str) -> int:
    value = data.get(key)
    if isinstance(value, list):
        return len(value)
    return 0


def _log(enabled: bool, message: str) -> None:
    if enabled:
        typer.echo(f"[view-aware-graph] {message}")


def _log_start(enabled: bool, message: str) -> float:
    started_at = perf_counter()
    if enabled:
        typer.echo(f"[view-aware-graph] {message} ...")
    return started_at


def _log_done(enabled: bool, message: str, started_at: float) -> None:
    if enabled:
        typer.echo(f"[view-aware-graph] {message} in {_elapsed(started_at)}")


def _elapsed(started_at: float) -> str:
    elapsed = perf_counter() - started_at
    if elapsed < 1:
        return f"{elapsed * 1000:.0f} ms"
    return f"{elapsed:.2f} s"


def _file_size(path: Path) -> int:
    return path.stat().st_size


def _format_vlm_adapter_error(error: VLMAdapterError, settings: VLMSettings) -> str:
    failure = error.failure
    message = (
        f"VLM request failed ({failure.error_type}) after {failure.attempts} attempts: "
        f"{failure.message}"
    )
    if failure.error_type == "timeout":
        return (
            f"{message}\n"
            f"Current timeout is {settings.timeout_seconds:g}s. "
            "For large local models such as qwen2.5vl:32b, try:\n"
            "  export VLM_TIMEOUT_SECONDS=1800\n"
            "Then rerun the same view-aware-graph extract command."
        )
    if failure.error_type == "connection_error":
        return (
            f"{message}\n"
            "Check that Ollama is running and reachable at the configured endpoint."
        )
    return message


@contextmanager
def _spinner(enabled: bool, message: str) -> Iterator[None]:
    if not enabled or not sys.stderr.isatty():
        started_at = _log_start(enabled, message)
        try:
            yield
        except BaseException:
            _log_done(enabled, "VLM request failed", started_at)
            raise
        finally:
            pass
        _log_done(enabled, "Received VLM response", started_at)
        return

    started_at = perf_counter()
    stop_event = Event()
    frames = cycle("|/-\\")

    def spin() -> None:
        while not stop_event.wait(0.1):
            frame = next(frames)
            elapsed = _elapsed(started_at)
            typer.echo(
                f"\r[view-aware-graph] {frame} {message} ({elapsed})",
                nl=False,
                err=True,
            )

    thread = Thread(target=spin, daemon=True)
    thread.start()
    try:
        yield
    except BaseException:
        stop_event.set()
        thread.join()
        typer.echo(
            f"\r[view-aware-graph] failed {message} after {_elapsed(started_at)}",
            err=True,
        )
        raise
    finally:
        if not stop_event.is_set():
            stop_event.set()
            thread.join()
            typer.echo(
                f"\r[view-aware-graph] done {message} in {_elapsed(started_at)}",
                err=True,
            )


if __name__ == "__main__":
    app()
