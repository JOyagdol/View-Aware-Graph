# View-Aware Graph Project Conventions

Last updated: 2026-05-12

## Purpose

View-Aware Graph extracts a structured, viewpoint-aware graph JSON from a single input image using a VLM. This repository owns only the image-to-graph stage.

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

The full pipeline is context for the final goal. Matching, retrieval, and localization/mapping are downstream concerns outside the current repository scope.

## Documentation Rules

- Root `AGENTS.md` is the detailed local Codex instruction file. It is intentionally ignored by Git, but it should mirror the important working rules from this document so Codex can automatically reference them.
- Maintain project documentation under `docs/`.
- English documentation under `docs/en/` is committed and treated as the repository source of truth.
- Korean documentation under `docs/ko/` must exist locally, but it is ignored by Git through `.gitignore`.
- Whenever a document changes, update both the English version and the Korean local version in the same working session.
- Every meaningful project change should document intent and result: what was created or changed, why it exists, and what the outcome was.
- Keep the task list in `docs/en/TODO.md` and the local Korean version in `docs/ko/TODO.md` current as work progresses.
- Use ISO dates (`YYYY-MM-DD`) for document updates and decision records.

## Project Structure

```text
.
|-- configs/                         # Runtime and experiment configuration
|-- data/
|   |-- raw/                         # Local input images; ignored except .gitkeep
|   |-- interim/                     # Local intermediate VLM outputs; ignored except .gitkeep
|   `-- processed/                   # Local graph outputs; ignored except .gitkeep
|-- docs/
|   |-- en/                          # Tracked English documentation
|   `-- ko/                          # Local Korean documentation; gitignored
|-- examples/
|   |-- images/                      # Small committed sample images only
|   `-- outputs/                     # Small committed sample graph JSON only
|-- prompts/                         # Versioned VLM prompt templates
|-- schemas/                         # JSON schemas for output contracts
|-- scripts/                         # CLI and utility scripts
|-- src/view_aware_graph/
|   |-- ingestion/                   # Image loading and input normalization
|   |-- vlm/                         # VLM provider adapters and prompt execution
|   |-- graph/                       # Graph models, validation, and transforms
|   `-- io/                          # JSON/config/file IO helpers
`-- tests/                           # Unit and integration tests
```

## Output Contract

- The canonical output is structured View-Aware Graph JSON.
- `schemas/view_aware_graph.schema.json` exists as a provisional output contract for this project stage, not as a downstream matching implementation.
- Generated graph JSON must include a `schema_version`.
- Generated graph JSON must preserve source image metadata, viewpoint assumptions, observed objects, relationships, confidence scores, and evidence text where available.
- Generated graph JSON should validate against `schemas/view_aware_graph.schema.json` before it is handed to downstream stages.
- Breaking schema changes require updating the schema, examples, tests, and both language versions of the docs.

## Code Conventions

- Use Python package code under `src/view_aware_graph/`.
- Keep VLM-provider-specific logic behind adapters in `src/view_aware_graph/vlm/`.
- Keep graph data contracts and transforms in `src/view_aware_graph/graph/`.
- Do not add retrieval, matching, or localization implementation to this repository unless the project scope is explicitly changed.
- Prefer typed functions and small modules with explicit inputs and outputs.
- Do not hard-code API keys, model names, local absolute paths, or user-specific paths.
- Store local credentials in `.env`, using `.env.example` as the template.
- Store repeatable configuration in `configs/`.
- Store prompts in `prompts/` and treat prompt edits as behavior changes.

## Git Conventions

- Use `main` as the default branch.
- Do not commit secrets, private datasets, large raw images, generated runs, or `docs/ko/`.
- Use short, scoped branch names:
  - `feat/<topic>`
  - `fix/<topic>`
  - `docs/<topic>`
  - `experiment/<topic>`
  - `chore/<topic>`
- Prefer Conventional Commit style:
  - `feat: add view graph schema`
  - `fix: validate missing edge confidence`
  - `docs: update project conventions`
  - `chore: initialize repository structure`
- Keep commits focused on one logical change.
- Before committing, run available checks and update `docs/en/TODO.md` plus the local Korean `docs/ko/TODO.md` when task state changes.

## Data Conventions

- `data/raw/`, `data/interim/`, and `data/processed/` are local work areas and ignored by Git except for `.gitkeep`.
- Small, non-sensitive examples may be committed under `examples/`.
- Any committed example must be minimal, reproducible, and safe to share.
- Large datasets and private imagery should be referenced in docs by location or acquisition method, not committed.

## Testing and Validation

- If Python code execution or testing is needed, tell the project owner first. The project owner will run Python commands inside their conda environment.
- Use conda as the only documented local setup path unless the project owner asks for a different environment strategy.
- Add tests under `tests/` for schema validation, graph transforms, and provider-independent parsing logic.
- Mock VLM calls in tests unless an explicit integration test is being run.
- Validate representative JSON outputs against `schemas/view_aware_graph.schema.json`.

## Change Checklist

- Code/config change is scoped and does not hard-code local machine details.
- Schema or prompt changes include matching docs and tests.
- New outputs or artifacts are either ignored or intentionally added as small examples.
- English docs are updated under `docs/en/`.
- Korean local docs are updated under `docs/ko/`.
- `docs/en/TODO.md` and `docs/ko/TODO.md` reflect current task state.
