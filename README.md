# View-Aware Graph

View-Aware Graph extracts a structured, viewpoint-aware graph JSON from a single input image using a VLM.

This repository owns the first stage of the broader city-scene localization pipeline:

```text
Input Image
  -> VLM
  -> Structured View-Aware Graph JSON
```

The downstream pipeline is kept as context only:

```text
Structured View-Aware Graph JSON
  -> Rule-based Cypher Query Generator
  -> Neo4j World Graph Retrieval
  -> Graph Similarity Matching
  -> Localization / Mapping
```

## Goal

Given an indoor scene image, the project aims to produce a machine-readable JSON graph that captures:

- visible scene objects
- viewpoint-aware spatial relationships
- object and relation confidence
- source image metadata
- evidence or uncertainty from the VLM response

The output contract is currently defined in [`schemas/view_aware_graph.schema.json`](schemas/view_aware_graph.schema.json).

## Repository Layout

```text
configs/                  Runtime and experiment configuration
data/                     Local data workspace; contents ignored by Git
docs/en/                  Tracked project documentation
examples/                 Small shareable sample inputs and outputs
prompts/                  VLM prompt templates
schemas/                  JSON schema contracts
scripts/                  CLI and utility scripts
src/view_aware_graph/     Python package source
tests/                    Test suite
```

See [`docs/en/CONVENTIONS.md`](docs/en/CONVENTIONS.md) for project rules, documentation policy, and structure conventions.

## Local Setup

Create the conda environment:

```powershell
conda env create -f environment.yml
```

Activate it:

```powershell
conda activate view-aware-graph
```

Run checks from inside the environment:

```powershell
pytest
```

If the environment already exists:

```powershell
conda env update -f environment.yml --prune
conda activate view-aware-graph
```

Python commands and tests are expected to be run by the project owner inside the conda environment.

## Configuration

Copy `.env.example` to `.env` for local VLM credentials and settings. Never commit `.env`.

Repeatable project defaults live in [`configs/default.toml`](configs/default.toml).

## Ubuntu Server Runtime

For the Proxmox Ubuntu 22.04 Server VM used for local Ollama/Qwen inference, see [`docs/en/UBUNTU_2204_SERVER_SETUP.md`](docs/en/UBUNTU_2204_SERVER_SETUP.md).

## Current Status

The repository is in the first pipeline design stage:

- project conventions are defined
- repository structure is initialized
- conda environment file is available
- general View-Aware Graph scheme is documented
- JSON schema is aligned to the indoor image-to-graph contract
- first GT-derived synthetic output example is available
- first VLM candidate shortlist and evaluation rubric are documented
- Ubuntu 22.04 Server runtime setup is documented for local Ollama inference
