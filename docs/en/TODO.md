# View-Aware Graph TODO

Last updated: 2026-05-22

## Completed Foundation

- [x] Create project convention rules.
- [x] Add detailed local `AGENTS.md` for Codex automatic reference and ignore it from Git.
- [x] Keep `docs/en/CONVENTIONS.md` as the tracked convention source.
- [x] Maintain local Korean docs under ignored `docs/ko/`.
- [x] Adapt Karpathy-inspired coding-agent principles into project conventions.
- [x] Initialize project structure for image-to-graph extraction only.
- [x] Initialize Git repository and push the initial project state.
- [x] Add conda-based environment setup and verify the environment locally.
- [x] Move Smart City Lab lobby GT/DT input images under ignored `data/raw/smartcitylab_lobby/`.
- [x] Assess GT/DT image suitability in `docs/en/EXAMPLE_INPUTS.md`.

## Active Development Goal

Build the first working pipeline for:

```text
Input Image
  -> VLM
  -> Structured View-Aware Graph JSON
```

The first development target is the local GT lobby image:

```text
data/raw/smartcitylab_lobby/SmartCityLab_Lobby_GT.jpg
```

## Phase 1: Ground The Expected Output

- [x] Create a small expected graph sketch for the GT image before writing provider-specific VLM code.
- [x] Decide the minimum node types needed for the first GT graph.
- [x] Decide the minimum relation types needed for the first GT graph.
- [x] Define the image/view coordinate convention for object positions and relations.
- [x] Decide how to represent uncertainty, occlusion, and VLM evidence text.
- [x] Document which GT image details should be ignored or down-weighted, such as monitor screen contents and visible people.
- [x] Decide not to extract people as View-Aware Graph nodes.
- [x] Prioritize furniture, wall, window/opening, door/opening nodes and their relations for the first benchmark.
- [x] Remove column/corridor as required graph node types; keep them only as observations or attributes when useful.
- [x] Treat ceiling cameras/lights/signs as `BuildingFurniture` world candidates rather than installation candidates.
- [x] Add 3DCitySG/CityGML world graph candidate type and relation hints without forcing final world classes.

Success criteria:

- A human-readable expected graph sketch exists.
- The sketch is small enough to guide prompt/schema design.
- The sketch only describes the current project output, not downstream matching.

## Phase 2: Refine The JSON Contract

- [x] Define the general View-Aware Graph scheme in `docs/en/VIEW_AWARE_GRAPH_SCHEME.md`.
- [x] Update `schemas/view_aware_graph.schema.json` from the general scheme.
- [x] Verify that the GT expected graph sketch is representable under the general scheme through a small synthetic example.
- [x] Add required top-level fields for source image metadata and view assumptions.
- [x] Add optional world alignment fields such as `world_candidate_types`, `world_alignment_note`, and relation-level `world_relation_hints`.
- [x] Finalize the first node taxonomy around furniture, wall, window/opening, and door/opening nodes.
- [x] Finalize the first relation taxonomy for view-aware spatial relationships.
- [x] Add a minimal valid sample JSON output under `examples/outputs/` if it is safe and synthetic.
- [x] Add schema notes to the docs when the contract changes.

Success criteria:

- The schema expresses the general View-Aware Graph scheme.
- The schema can express the expected GT graph without being overfit to it.
- The schema remains provider-independent.
- The schema does not include downstream retrieval, matching, or localization logic.

## Phase 3: Select And Evaluate VLM Baseline

- [x] Define VLM model selection criteria: vision quality, structured JSON reliability, spatial relation reasoning, cost, latency, API stability, and privacy constraints.
- [x] List candidate VLM providers/models without hard-coding one into the project.
- [x] Create a small evaluation rubric based on the GT expected graph sketch.
- [x] Decide the initial free-first baseline model for the first implementation.
- [x] Record why the baseline model was chosen and what risks remain.
- [x] Keep provider/model settings configurable through config or environment variables.

Success criteria:

- A baseline VLM is selected for the first working pipeline.
- Selection is based on the GT image task, not generic benchmark claims alone.
- The repository remains provider-neutral even after a baseline model is selected.

## Phase 4: Prompt Design

- [x] Write the first production-oriented extraction prompt in `prompts/view_graph_extraction.md`.
- [x] Require JSON-only VLM output.
- [x] Instruct the VLM to preserve evidence and uncertainty.
- [x] Instruct the VLM to focus on stable architectural and scene elements.
- [x] Instruct the VLM to avoid over-indexing on monitor screen contents unless explicitly relevant.
- [ ] Prepare a prompt checklist for GT and DT input trials.

Success criteria:

- Prompt output target matches the schema.
- Prompt can be tested on the GT image by the project owner.
- Prompt is documented as behavior-changing project logic.

## Phase 5: Provider-Neutral VLM Interface

- [ ] Define a provider-neutral VLM adapter interface under `src/view_aware_graph/vlm/`.
- [ ] Define request and response data models.
- [ ] Read provider/model settings from config or environment, not hard-coded values.
- [ ] Define where raw VLM responses should be stored under ignored local outputs.
- [ ] Define retry and failure reporting behavior.

Success criteria:

- VLM provider code is isolated behind an adapter.
- The rest of the project can work with parsed graph JSON without knowing the provider.
- No API key, model name, or local path is hard-coded.

## Phase 6: Parsing And Validation

- [ ] Implement JSON extraction/parsing from VLM responses.
- [ ] Implement schema validation for generated graph JSON.
- [ ] Return useful validation errors for missing fields, invalid node types, and invalid relations.
- [ ] Add tests for provider-independent parsing and validation logic.

Success criteria:

- Invalid VLM outputs fail clearly.
- Valid outputs pass schema validation.
- Python tests are prepared, and the project owner runs them in conda.

## Phase 7: Local CLI Workflow

- [ ] Add a minimal CLI entry point for image-to-graph extraction.
- [ ] Accept input image path, config path, and output path.
- [ ] Write graph JSON outputs under ignored local output directories by default.
- [ ] Document the CLI workflow without committing generated outputs.

Success criteria:

- The project owner can run one command to process the GT image.
- Generated outputs are ignored unless intentionally promoted to small examples.

## Phase 8: VLM Output Improvement Loop

- [ ] Run the baseline VLM on the GT input and compare output against the expected graph sketch.
- [ ] Classify errors: missing objects, hallucinated objects, wrong relations, bad confidence, invalid JSON, and weak evidence.
- [ ] Improve prompt instructions based on observed errors.
- [ ] Improve schema constraints or parser feedback when failures are structural.
- [ ] Re-run GT evaluation after each prompt/schema/parser change.
- [ ] Track improvement decisions in docs.
- [ ] Consider fine-tuning, distillation, or a smaller local model only after enough curated input/output pairs exist.

Success criteria:

- Improvement is measured against the expected graph sketch and schema validation.
- Prompt/schema/parser changes are separated from model selection changes.
- Fine-tuning is treated as a later option, not the first improvement step.

## Phase 9: GT/DT Comparison

- [ ] Run the extraction flow on the GT lobby image.
- [ ] Run the extraction flow on the DT lobby image.
- [ ] Document differences between GT and DT graph quality.
- [ ] Decide whether DT render improvements are needed before using it as a recurring benchmark.

Success criteria:

- GT is the primary extraction benchmark.
- DT is used as a secondary synthetic/real robustness check.
- The comparison stays inside the image-to-graph project scope.

## Current Next Step

- [ ] Project owner runs schema validation with `python3.11` on the Ubuntu server for `examples/outputs/smartcitylab_lobby_gt_minimal.json`.
- [ ] Prepare an inference-only local/free VLM smoke test path for Qwen2.5-VL-3B-Instruct, then Qwen2.5-VL-7B-Instruct.
- [ ] Prepare a 32GB VRAM local test path for Qwen2.5-VL-32B-Instruct quantized and Qwen3-VL-32B-Instruct quantized.
- [ ] Start Phase 5: define the provider-neutral VLM adapter interface under `src/view_aware_graph/vlm/` with local/free and paid-provider implementations separated.
