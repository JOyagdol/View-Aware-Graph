# CLI Workflow

Last updated: 2026-05-28

## Purpose

This document records the first local command-line workflow for View-Aware Graph extraction.

The CLI stays inside the current repository scope:

```text
Input Image
  -> VLM
  -> Structured View-Aware Graph JSON
```

It does not implement downstream Cypher generation, Neo4j retrieval, graph matching, localization, or mapping.

## Command

After installing the project in the configured Python environment, run:

For the current 7B local baseline:

```bash
export VLM_PROVIDER=ollama
export VLM_MODEL=qwen2.5vl:7b

view-aware-graph extract \
  --image data/raw/smartcitylab_lobby/SmartCityLab_Lobby_GT.jpg \
  --config configs/default.toml \
  --output data/processed/view_graphs/smartcitylab_lobby_gt_cli.json \
  --run-id smartcitylab_lobby_gt_cli \
  --verbose
```

For the 32B local comparison run:

```bash
export VLM_PROVIDER=ollama
export VLM_MODEL=qwen2.5vl:32b
export VLM_TIMEOUT_SECONDS=1800

view-aware-graph extract \
  --image data/raw/smartcitylab_lobby/SmartCityLab_Lobby_GT.jpg \
  --config configs/default.toml \
  --output data/processed/view_graphs/smartcitylab_lobby_gt_qwen2_5vl_32b_cli.json \
  --run-id smartcitylab_lobby_gt_qwen2_5vl_32b_cli \
  --verbose
```

If the shell says `view-aware-graph: command not found`, reinstall the editable package after the console script has been added:

```bash
pip install -e .[dev]
```

Fallback module form:

```bash
python3.11 -m view_aware_graph extract \
  --image data/raw/smartcitylab_lobby/SmartCityLab_Lobby_GT.jpg \
  --config configs/default.toml \
  --output data/processed/view_graphs/smartcitylab_lobby_gt_cli.json \
  --run-id smartcitylab_lobby_gt_cli \
  --verbose
```

The CLI:

- loads VLM settings from config and environment variables
- reads the extraction prompt
- sends the image and prompt through the configured adapter
- writes raw provider output under `data/interim/vlm_raw/`
- parses graph JSON from the provider response
- validates against `schemas/view_aware_graph.schema.json`
- applies deterministic common relation repairs by default
- writes validated graph JSON under `data/processed/view_graphs/`
- writes a PNG graph overlay next to the graph JSON by default

Visualization output defaults to the graph output path with a `.png` suffix. The
overlay uses node center points and edge arrows instead of full bbox rectangles,
so the original image remains easy to inspect:

```text
data/processed/view_graphs/<run_id>.png
```

To choose a custom visualization path:

```bash
view-aware-graph extract \
  --image data/raw/smartcitylab_lobby/SmartCityLab_Lobby_GT.jpg \
  --config configs/default.toml \
  --output data/processed/view_graphs/smartcitylab_lobby_gt_cli.json \
  --visualization data/processed/view_graphs/smartcitylab_lobby_gt_cli_overlay.png
```

If the custom path ends in `.svg`, the same overlay can still be written as SVG.

To regenerate only the visualization from an existing graph JSON without calling
the VLM again:

```bash
view-aware-graph visualize \
  --graph data/processed/view_graphs/smartcitylab_lobby_gt_qwen2_5vl_32b_cli.json \
  --image data/raw/smartcitylab_lobby/SmartCityLab_Lobby_GT.jpg \
  --output data/processed/view_graphs/smartcitylab_lobby_gt_qwen2_5vl_32b_cli.png
```

To skip visualization:

```bash
view-aware-graph extract \
  --image data/raw/smartcitylab_lobby/SmartCityLab_Lobby_GT.jpg \
  --config configs/default.toml \
  --run-id smartcitylab_lobby_gt_cli \
  --no-visualization
```

## Required Environment

For the current local Ollama adapter:

```bash
export VLM_PROVIDER=ollama
export VLM_MODEL=qwen2.5vl:7b
```

Optional override:

```bash
export VLM_ENDPOINT=http://127.0.0.1:11434/api/generate
export VLM_TIMEOUT_SECONDS=1800
```

`VLM_TIMEOUT_SECONDS` is useful for large local vision models. The default config is
`600` seconds, and the 32B comparison run may need a longer timeout when Ollama
has to load the model or the GPU is busy.

## Output Policy

Generated raw and processed outputs are local artifacts.

They should remain ignored by Git unless explicitly promoted as small, safe examples.

Expected output locations:

```text
data/interim/vlm_raw/<run_id>_raw.json
data/processed/view_graphs/<run_id>.json
data/processed/view_graphs/<run_id>.png
```

## Validation Failures

If schema validation fails, the CLI prints readable validation issues and stops before writing the processed graph output.

Common relation vocabulary drift, such as `partially_occluded_by`, should be handled by validation and repair logic rather than expanding the schema too early.

The CLI currently applies this common repair by default:

```text
partially_occluded_by
  -> relation: behind
  -> uncertainty: ["occluded", "viewpoint_inferred"]
```

Disable deterministic repair when inspecting raw model behavior:

```bash
view-aware-graph extract \
  --image data/raw/smartcitylab_lobby/SmartCityLab_Lobby_GT.jpg \
  --config configs/default.toml \
  --run-id smartcitylab_lobby_gt_no_repair \
  --no-repair-common-relations
```

## Progress Logs

The CLI prints progress logs by default. During the blocking Ollama request, an interactive terminal shows a spinner with elapsed time. Non-interactive output falls back to start/done step logs.

Logged steps include:

- settings loading
- prompt loading
- VLM request start
- raw response write
- graph JSON parsing
- schema validation
- common repair attempt
- graph output write

Each progress log includes elapsed time when the step completes. The VLM request step also reports the input image size, and output write steps report file sizes.
