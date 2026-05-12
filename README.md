# View-Aware Graph

View-Aware Graph converts an input image into a structured scene graph JSON that is aware of the camera/viewpoint.

Current project scope:

```text
Input Image
  -> VLM
  -> Structured View-Aware Graph JSON
```

Broader downstream context:

```text
Input Image
  -> VLM
  -> Structured View-Aware Graph JSON
  -> Rule-based Cypher Query Generator
  -> Neo4j World Graph Retrieval
  -> Graph Similarity Matching
  -> Localization / Mapping
```

## Repository Layout

See [docs/en/CONVENTIONS.md](docs/en/CONVENTIONS.md) for the project rules, documentation policy, and full structure.

## Local Setup

```powershell
conda env create -f environment.yml
conda activate view-aware-graph
pytest
```

Python commands are expected to be run by the project owner inside the conda environment.

Copy `.env.example` to `.env` for local VLM credentials. Never commit `.env`.
