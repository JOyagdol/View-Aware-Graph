# View-Aware Graph

View-Aware Graph extracts a structured, viewpoint-aware graph JSON from a single image using a Vision-Language Model.

```text
Input Image
  -> VLM
  -> Structured View-Aware Graph JSON
```

This repository owns only the image-to-graph extraction stage. Downstream Cypher generation, Neo4j retrieval, graph similarity matching, localization, and mapping are intentionally out of scope here.

## What It Produces

The target output is schema-valid JSON containing:

- source image metadata
- viewpoint assumptions
- observed scene nodes
- view-aware spatial relations
- confidence values
- visual evidence text
- uncertainty and occlusion notes when available

The current output contract is [`schemas/view_aware_graph.schema.json`](schemas/view_aware_graph.schema.json).

## Current Capabilities

- Versioned extraction prompt in [`prompts/view_graph_extraction.md`](prompts/view_graph_extraction.md)
- Provider-neutral VLM request/response interface
- Local Ollama adapter for Qwen vision models
- CLI workflow through `view-aware-graph extract`
- JSON parsing from VLM/Ollama responses
- JSON Schema validation with readable errors
- Conservative repair for common relation vocabulary drift
- Unit tests for parsing, validation, adapter behavior, and CLI workflow

## Not Included

This repository does not implement:

- Cypher query generation
- Neo4j world graph retrieval
- graph similarity matching
- localization or mapping
- model fine-tuning
- private image or dataset publication

Fine-tuning may be considered later only after enough curated image/GT-graph pairs exist.

## Setup

Create and activate the conda environment:

```bash
conda env create -f environment.yml
conda activate view-aware-graph
```

If the environment already exists:

```bash
conda env update -f environment.yml --prune
conda activate view-aware-graph
```

Install the package in editable mode:

```bash
pip install -e .[dev]
```

Run checks:

```bash
ruff check .
mypy
pytest
```

## Local Ollama Run

Set the local adapter environment:

```bash
export VLM_PROVIDER=ollama
export VLM_MODEL=qwen2.5vl:7b
```

Run the GT lobby image:

```bash
view-aware-graph extract \
  --image data/raw/smartcitylab_lobby/SmartCityLab_Lobby_GT.jpg \
  --config configs/default.toml \
  --output data/processed/view_graphs/smartcitylab_lobby_gt_cli.json \
  --run-id smartcitylab_lobby_gt_cli \
  --verbose
```

For the 32B comparison run:

```bash
export VLM_MODEL=qwen2.5vl:32b
export VLM_TIMEOUT_SECONDS=1800

view-aware-graph extract \
  --image data/raw/smartcitylab_lobby/SmartCityLab_Lobby_GT.jpg \
  --config configs/default.toml \
  --output data/processed/view_graphs/smartcitylab_lobby_gt_qwen2_5vl_32b_cli.json \
  --run-id smartcitylab_lobby_gt_qwen2_5vl_32b_cli \
  --verbose
```

Generated raw and processed outputs are written under ignored local directories:

```text
data/interim/vlm_raw/
data/processed/view_graphs/
```

The CLI also writes a PNG graph overlay next to the graph JSON by default:

```text
data/processed/view_graphs/<run_id>.png
```

## Documentation

- Project rules: [`docs/en/CONVENTIONS.md`](docs/en/CONVENTIONS.md)
- Graph scheme: [`docs/en/VIEW_AWARE_GRAPH_SCHEME.md`](docs/en/VIEW_AWARE_GRAPH_SCHEME.md)
- CLI workflow: [`docs/en/CLI_WORKFLOW.md`](docs/en/CLI_WORKFLOW.md)
- VLM interface: [`docs/en/VLM_INTERFACE.md`](docs/en/VLM_INTERFACE.md)
- Model candidates: [`docs/en/VLM_MODEL_CANDIDATES.md`](docs/en/VLM_MODEL_CANDIDATES.md)
- Evaluation rubric: [`docs/en/VLM_EVALUATION_RUBRIC.md`](docs/en/VLM_EVALUATION_RUBRIC.md)
- Current tasks: [`docs/en/TODO.md`](docs/en/TODO.md)

## Data Policy

Local raw images, raw VLM responses, generated graph outputs, and Korean local documentation are ignored by Git by default. Only small, safe examples should be committed intentionally.
