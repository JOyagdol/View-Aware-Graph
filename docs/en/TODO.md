# View-Aware Graph TODO

Last updated: 2026-05-28

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
- [x] Prepare a prompt checklist for GT and DT input trials.

Success criteria:

- Prompt output target matches the schema.
- Prompt can be tested on the GT image by the project owner.
- Prompt is documented as behavior-changing project logic.

## Phase 5: Provider-Neutral VLM Interface

- [x] Define a provider-neutral VLM adapter interface under `src/view_aware_graph/vlm/`.
- [x] Define request and response data models.
- [x] Read provider/model settings from config or environment, not hard-coded values.
- [x] Define where raw VLM responses should be stored under ignored local outputs.
- [x] Define retry and failure reporting behavior.

Success criteria:

- VLM provider code is isolated behind an adapter.
- The rest of the project can work with parsed graph JSON without knowing the provider.
- No API key, model name, or local path is hard-coded.

## Phase 6: Parsing And Validation

- [x] Implement JSON extraction/parsing from VLM responses.
- [x] Implement schema validation for generated graph JSON.
- [x] Return useful validation errors for missing fields, invalid node types, and invalid relations.
- [x] Add tests for provider-independent parsing and validation logic.

Success criteria:

- Invalid VLM outputs fail clearly.
- Valid outputs pass schema validation.
- Python tests are prepared, and the project owner runs them in conda.

## Phase 7: Local CLI Workflow

- [x] Add a minimal CLI entry point for image-to-graph extraction.
- [x] Accept input image path, config path, and output path.
- [x] Write graph JSON outputs under ignored local output directories by default.
- [x] Document the CLI workflow without committing generated outputs.

Success criteria:

- The project owner can run one command to process the GT image.
- Generated outputs are ignored unless intentionally promoted to small examples.

## Phase 8: VLM Output Improvement Loop

- [x] Run the baseline VLM on the GT input and compare output against the expected graph sketch.
- [x] Classify errors: missing objects, hallucinated objects, wrong relations, bad confidence, invalid JSON, and weak evidence.
- [x] Improve prompt instructions based on observed errors.
- [x] Improve schema constraints or parser feedback when failures are structural.
- [x] Re-run GT evaluation after each prompt/schema/parser change.
- [x] Track improvement decisions in docs.
- [ ] If larger local models remain weak, collect project-owner drawn GT graph annotations for the lobby image.
- [ ] Convert drawn GT graph annotations into schema-valid JSON annotation files in an ignored local data area.
- [ ] Compare VLM outputs against the owner-drawn GT annotation before considering training.
- [ ] Consider fine-tuning, distillation, or a smaller local model only after enough curated input/output pairs exist.

Success criteria:

- Improvement is measured against the expected graph sketch and schema validation.
- Prompt/schema/parser changes are separated from model selection changes.
- Fine-tuning is treated as a later option, not the first improvement step.

## Phase 8.5: Quality Hardening

Improve the reliability, inspectability, and evaluation quality of the current working pipeline before moving to GT annotation datasets or fine-tuning.

### A. CLI And Adapter Robustness

- [x] Compare Qwen2.5-VL-7B and Qwen2.5-VL-32B CLI outputs on the same GT input.
- [ ] Strengthen CLI error messages for parse failures, schema failures, adapter failures, and missing config/model settings.
- [ ] Add an Ollama health/model availability check before long image extraction runs.
- [ ] Improve missing Ollama server and missing model messages with actionable commands such as `ollama list` and `ollama pull`.
- [ ] Decide output overwrite policy for existing raw, graph, and report files.
- [ ] Consider a `--dry-run` mode that validates config, prompt path, image path, provider, model, and output paths without calling the VLM.
- [ ] Define CLI exit code policy for success, parse failure, schema failure, adapter failure, and configuration failure.
- [ ] Ensure raw provider output is saved whenever a provider response exists, even if parsing or schema validation later fails.

### B. Run Artifacts And Reproducibility

- [ ] Save a compact run summary for each CLI run: provider, model, prompt path, config path, input image, raw response path, graph output path, schema result, repair count, node count, edge count, and elapsed time.
- [ ] Add prompt/config/model metadata to generated graph outputs or sidecar run reports without changing the core graph schema prematurely.
- [ ] Store run sidecar reports next to graph outputs, such as `data/processed/view_graphs/<run_id>.report.json`.
- [ ] Record prompt file hash, config file hash, schema version, provider, model, endpoint, run id, start time, end time, and elapsed seconds.
- [ ] Record raw response size, graph output size, validation status, repair status, node count, edge count, and relation type counts.
- [ ] Keep run reports local/ignored by default unless explicitly promoted as small safe examples.

### C. Validation And Repair Auditability

- [ ] Make repair behavior auditable by recording which repair rules were applied and where.
- [ ] Record validation issues in machine-readable report form, including path, validator, message, offending value, and suggestion.
- [ ] Record repair before/after values in report form.
- [ ] Document repair policy: repairs may normalize schema vocabulary drift but must not invent new objects or unsupported relations.
- [x] Add deterministic repair coverage for observed 32B schema drift: object-style `global_observations`, object-style `region.bbox_2d`, and occluder-id list `occlusion`.
- [ ] Add tests for repair report contents using observed relation and field-shape drift.
- [ ] Decide whether repaired graph outputs should overwrite the requested output path or write separate repaired candidate files.

### D. Evaluation Summary And Metrics

- [ ] Add a small evaluation report command or helper that summarizes nodes, edges, relation types, subtype coverage, uncertainty coverage, and repair count.
- [x] Add default PNG overlay output so graph quality can be inspected visually next to the JSON.
- [x] Switch visualization from bbox rectangles to node center points with edge arrows.
- [x] Add a visualization-only CLI command for regenerating overlays from existing graph JSON.
- [ ] Review common 2D scene graph evaluation metrics and decide which are appropriate for View-Aware Graph outputs.
- [ ] Add initial metric candidates for object/node detection, relation predicate accuracy, triplet matching, graph edit distance or graph similarity, and schema/constraint validity.
- [ ] Keep 2D scene graph metrics separate from downstream localization or world-graph matching metrics.
- [ ] Document which metrics require exact manual GT annotations and which can be used for rough prompt iteration.
- [ ] Implement GT-free weak summary metrics first: node count, edge count, subtype coverage, uncertainty coverage, confidence distribution, relation type distribution, schema validity, and repair count.
- [ ] Define GT-required metrics later: node precision/recall, relation predicate accuracy, subject-predicate-object triplet precision/recall, graph edit distance, and graph similarity.
- [x] Add a first comparison report format for 7B vs 32B outputs before implementing full automatic scoring.

### E. Owner-Drawn GT Annotation Readiness

- [ ] Define owner-drawn GT annotation storage policy under ignored local data paths.
- [ ] Define a first GT-vs-output comparison report format before implementing automatic scoring.
- [ ] Define a human annotation template: image reference, node ids, node labels/types/subtypes, regions, occlusion, relations, ignored elements, and uncertainty notes.
- [ ] Decide whether owner-drawn GT annotations should include approximate bounding boxes, coarse regions only, or both.
- [ ] Convert the first owner-drawn GT annotation into schema-valid JSON before using it for evaluation or training.
- [ ] Keep training/fine-tuning blocked until multiple curated image/GT graph pairs exist and repeated failure patterns are documented.

Success criteria:

- CLI runs produce enough metadata to reproduce and compare results.
- Repairs are visible and auditable rather than hidden.
- Evaluation has a documented metric plan grounded in 2D scene graph practice.
- Owner-drawn GT annotation can start with a clear storage and comparison policy.
- Fine-tuning remains blocked until enough curated image/GT graph pairs and repeated failure patterns exist.

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

- [x] Project owner confirmed schema validation passed for the first `qwen2.5vl:7b` GT output.
- [x] Prepare an inference-only local/free VLM smoke test path for Qwen2.5-VL-7B-Instruct.
- [ ] Prepare a 32GB VRAM local test path for Qwen2.5-VL-32B-Instruct quantized and Qwen3-VL-32B-Instruct quantized.
- [x] Add configurable Ollama request timeout for large local model runs.
- [x] Run Qwen2.5-VL-32B on the GT image through the CLI and compare against the Qwen2.5-VL-7B CLI result.
- [x] Improve the extraction prompt based on the first Qwen2.5-VL-7B GT error labels: `missing_core_object`, `wrong_relation`, `weak_evidence`, `missing_uncertainty`, `missing_subtype`, `uniform_confidence`, and `source_target_evidence_mismatch`.
- [x] Re-run Qwen2.5-VL-7B on the GT image after prompt improvement and compare against the first baseline output.
- [x] Decide whether to run one prompt v3 iteration or start Phase 5 provider-neutral interface implementation.
- [x] Run one prompt v3 iteration focused on required monitor subtype, region/depth/occlusion fields, varied confidence, support edges, and foreground occlusion.
- [x] Confirm prompt v3 repaired output passes schema validation after mapping `partially_occluded_by` to `behind` with occlusion uncertainty.
- [x] Start Phase 5: define the provider-neutral VLM adapter interface under `src/view_aware_graph/vlm/` with local/free and paid-provider implementations separated.
- [x] Start Phase 6: implement provider-independent JSON parsing, schema validation, and clear enum mismatch error reporting.
- [ ] Project owner runs `pytest` in the configured Python environment.
- [ ] Project owner runs `ruff check .` and `mypy` after Phase 5 interface additions.
- [x] Define concrete retry and failure reporting behavior before adding a real Ollama adapter.
- [x] Decide whether to implement a concrete Ollama adapter or start the minimal CLI workflow next.
- [x] Implement concrete Ollama adapter with injected-transport unit tests.
- [ ] Project owner runs `ruff check .`, `mypy`, and `pytest` after the Ollama adapter addition.
- [x] Start Phase 7 minimal CLI workflow after adapter checks pass.
- [ ] Project owner runs `ruff check .`, `mypy`, and `pytest` after the CLI workflow addition.
- [ ] Project owner runs a local CLI smoke test with `view-aware-graph extract`.
- [ ] If Qwen2.5-VL-32B quality is still weak, start an owner-drawn GT annotation pass before any fine-tuning decision.
- [x] After the 32B GT run, start Phase 8.5 Quality Hardening before owner-drawn GT annotation and fine-tuning work.
- [x] Decide that Qwen2.5-VL-32B is not sufficient as a final extractor and needs owner-drawn GT annotation support.
- [ ] Next Quality Hardening task: implement run summary/report sidecar for CLI runs.
- [ ] Next metric task: choose the first GT-free summary metrics under Phase 8.5 D before manual GT scoring.
