# VLM Evaluation Rubric

Last updated: 2026-05-28

## Purpose

This rubric defines the first fast evaluation pass for VLM outputs on the Smart City Lab lobby GT image.

It evaluates only:

```text
Input Image
  -> VLM
  -> Structured View-Aware Graph JSON
```

It does not evaluate downstream retrieval, graph matching, localization, or mapping.

## Test Input

Primary local input:

```text
data/raw/smartcitylab_lobby/SmartCityLab_Lobby_GT.jpg
```

Reference documents:

- `schemas/view_aware_graph.schema.json`
- `docs/en/VIEW_AWARE_GRAPH_SCHEME.md`
- `docs/en/EXPECTED_GRAPH_SKETCH_SMARTCITYLAB_LOBBY_GT.md`
- `examples/outputs/smartcitylab_lobby_gt_minimal.json`

## Pass/Fail Gates

An output fails immediately if:

- it is not valid JSON
- it cannot validate against `schemas/view_aware_graph.schema.json`
- it extracts a person as a graph node
- it adds downstream matching, Neo4j, Cypher, localization, or mapping fields
- it replaces image-observed node `type` values with final CityGML classes

## Score Categories

Score each category from 0 to 2.

| Category | 0 | 1 | 2 |
| --- | --- | --- | --- |
| Core objects | Misses most primary objects | Finds some core objects | Finds wall, door/opening, floor, foreground monitor/display objects as `object` nodes, and at least one furniture/surface/panel node |
| Spatial relations | Mostly absent or wrong | Some useful image-plane relations | Captures left/right, above/below, foreground occlusion, and support/attachment relations |
| Schema fit | Requires heavy repair | Minor repair needed | Valid as-is |
| Evidence | Generic or unsupported | Some visible evidence | Short, concrete evidence grounded in the image |
| Uncertainty | Missing or misleading | Partial uncertainty | Correctly marks occlusion, reflection, screen content, and inferred depth |
| Scope control | Includes downstream logic or people nodes | Mostly scoped but noisy | Strictly image-to-graph; people ignored as nodes |

Maximum score: 12.

Recommended interpretation:

- 10-12: strong baseline
- 7-9: usable with prompt/schema iteration
- 4-6: weak baseline
- 0-3: unsuitable for first implementation

## Error Labels

Use these labels when recording failures:

- `invalid_json`
- `schema_mismatch`
- `missing_core_object`
- `hallucinated_object`
- `wrong_relation`
- `people_as_nodes`
- `screen_content_overfocus`
- `weak_evidence`
- `missing_uncertainty`
- `downstream_scope_leak`

## First Candidate Run Order

1. Qwen2.5-VL-3B-Instruct for a fast free smoke test
2. Qwen2.5-VL-7B-Instruct as the primary free local baseline
3. Qwen2.5-VL-32B-Instruct quantized as the stable 32GB-class local baseline
4. Qwen3-VL-32B-Instruct quantized as the best 32GB-class local quality target if runtime/memory allows
5. SmolVLM-class lightweight model if Qwen is too heavy
6. Optional local comparison with InternVL3-8B or Gemma 3 vision-capable variants
7. Paid upgrade to OpenAI latest GPT vision-capable model after local/free failures are understood
8. Optional paid cross-provider validation with Claude or Gemini

## First Baseline Trial Record

Date: 2026-05-28

Model:

```text
qwen2.5vl:7b
```

Input:

```text
data/raw/smartcitylab_lobby/SmartCityLab_Lobby_GT.jpg
```

Outputs:

```text
data/interim/vlm_raw/qwen2_5vl_7b_smartcitylab_lobby_gt_raw.json
data/processed/view_graphs/qwen2_5vl_7b_smartcitylab_lobby_gt.json
```

Schema result:

- Project owner confirmed schema validation passed.

Approximate rubric score:

- Core objects: 1/2
- Spatial relations: 0-1/2
- Schema fit: 2/2
- Evidence: 1/2
- Uncertainty: 0/2
- Scope control: 2/2
- Total: about 6/12

Observed strengths:

- Valid JSON was produced.
- Output stayed within image-to-graph scope.
- People were not extracted as graph nodes.
- Coarse schema node types were respected.

Observed failure labels:

- `missing_core_object`
- `wrong_relation`
- `weak_evidence`
- `missing_uncertainty`
- `missing_subtype`
- `uniform_confidence`
- `source_target_evidence_mismatch`

Decision:

- Treat this as a useful weak baseline.
- Improve the prompt before testing larger local models or paid providers.
- Prioritize meaningful node ids, monitor subtypes, left/right monitor separation, foreground occlusion, uncertainty, and relation evidence alignment.

## Prompt V2 Trial Record

Date: 2026-05-28

Model:

```text
qwen2.5vl:7b
```

Input:

```text
data/raw/smartcitylab_lobby/SmartCityLab_Lobby_GT.jpg
```

Outputs:

```text
data/interim/vlm_raw/qwen2_5vl_7b_smartcitylab_lobby_gt_prompt_v2_raw.json
data/processed/view_graphs/qwen2_5vl_7b_smartcitylab_lobby_gt_prompt_v2.json
```

Schema result:

- Project owner confirmed schema validation passed.

Approximate rubric score:

- Core objects: 1/2
- Spatial relations: 1/2
- Schema fit: 2/2
- Evidence: 1/2
- Uncertainty: 0/2
- Scope control: 2/2
- Total: about 7/12

Observed improvements over the first baseline:

- Meaningful node ids were used instead of numeric ids.
- Left and right monitor nodes were separated.
- Display stand nodes were included.
- JSON remained schema-valid and scoped to image-to-graph extraction.

Remaining failure labels:

- `missing_core_object`
- `wrong_relation`
- `weak_evidence`
- `missing_uncertainty`
- `missing_subtype`
- `uniform_confidence`
- `source_target_evidence_mismatch`

Decision:

- Treat prompt v2 as an improvement, but not yet a strong benchmark output.
- A prompt v3 should use stronger requirements for monitor `subtype`, `region`, `depth_hint`, `occlusion`, `uncertainty`, varied confidence, and foreground occlusion relations.
- Parser/schema repair is not urgent yet because both baseline and v2 outputs were valid JSON and passed schema validation.

## Prompt V3 Trial Record

Date: 2026-05-28

Model:

```text
qwen2.5vl:7b
```

Input:

```text
data/raw/smartcitylab_lobby/SmartCityLab_Lobby_GT.jpg
```

Outputs:

```text
data/interim/vlm_raw/qwen2_5vl_7b_smartcitylab_lobby_gt_prompt_v3_raw.json
data/processed/view_graphs/qwen2_5vl_7b_smartcitylab_lobby_gt_prompt_v3.json
data/processed/view_graphs/qwen2_5vl_7b_smartcitylab_lobby_gt_prompt_v3_repaired.json
```

Schema result:

- Original prompt v3 output failed schema validation because one edge used `relation: "partially_occluded_by"`, which is outside the allowed relation taxonomy.
- A minimal repaired copy changed that relation to `behind` and added `uncertainty: ["occluded", "viewpoint_inferred"]`.
- Project owner confirmed the repaired copy passed schema validation.

Approximate rubric score after minimal repair:

- Core objects: 2/2
- Spatial relations: 2/2
- Schema fit: 1/2
- Evidence: 1/2
- Uncertainty: 1/2
- Scope control: 2/2
- Total: about 9/12

Observed improvements over prompt v2:

- Central wall, floor, center-left door, left monitor, right monitor, right display stand, and right shelf/furniture nodes were captured.
- Monitor nodes included `subtype: "monitor"`.
- Foreground occlusion was represented through `in_front_of` edges from monitors to the central wall.
- The support relation was correctly represented as `display_stand_right supports monitor_right`.
- Confidence values varied across obvious, clear, and partially occluded observations.

Remaining failure labels:

- `schema_mismatch`
- `weak_evidence`
- `missing_uncertainty`
- `missing_required_optional_detail`

Decision:

- Treat prompt v3 repaired output as the strongest current Qwen2.5-VL-7B GT result.
- Stop prompt-only iteration for now and move toward provider-neutral parsing, validation, and repair/error reporting.
- The enum mismatch shows that Phase 6 should provide clear validation errors and possibly deterministic repair suggestions for common relation vocabulary drift.

## Qwen2.5-VL-32B CLI Trial Record

Date: 2026-05-28

Model:

```text
qwen2.5vl:32b
```

Input:

```text
data/raw/smartcitylab_lobby/SmartCityLab_Lobby_GT.jpg
```

Outputs:

```text
data/interim/vlm_raw/smartcitylab_lobby_gt_qwen2_5vl_32b_cli_raw.json
data/processed/view_graphs/smartcitylab_lobby_gt_qwen2_5vl_32b_cli.json
data/processed/view_graphs/smartcitylab_lobby_gt_qwen2_5vl_32b_cli.png
```

Schema result:

- Final CLI output validated after prompt tightening and deterministic field-shape repair support.
- The output contains 8 nodes and 6 edges.

Approximate rubric score:

- Core objects: 1/2
- Spatial relations: 1/2
- Schema fit: 2/2
- Evidence: 1/2
- Uncertainty: 1/2
- Scope control: 2/2
- Total: about 8/12

Observed strengths:

- Captured central wall, floor, center-left door, right foreground monitor, right display stand, right shelf/furniture, left wall panel, and ceiling.
- Used valid coarse node types and monitor subtype.
- Included useful relations: `attached_to`, `supports`, `in_front_of`, `behind`, `part_of`, and `above`.
- Stayed within image-to-graph scope and did not extract people as nodes.

Observed limitations:

- The left foreground monitor was missed.
- Large architectural nodes such as wall, door, floor, and ceiling often use coarse regions rather than precise `bbox_2d`, so visualization is less informative.
- The graph is still sparse for scene understanding; important wall/door geometry is not strongly localized.
- One edge id names the relation in a confusing order, although the actual `source`, `target`, and `relation` fields are semantically correct.

Remaining failure labels:

- `missing_core_object`
- `missing_required_optional_detail`
- `weak_evidence`
- `coarse_region_only`
- `sparse_relation_graph`

Decision:

- Treat this as the current 32B baseline, not as a satisfactory final extractor.
- Stop simply scaling local model size for now.
- Move to Phase 8.5 Quality Hardening and owner-drawn GT annotation readiness.

## 7B Versus 32B Comparison Summary

Date: 2026-05-28

Summary:

- The repaired 7B prompt v3 output captured both left and right monitors, but needed relation repair.
- The 32B CLI output was schema-valid and structurally cleaner, but missed the left monitor and kept major architectural nodes too coarse.
- 32B improved JSON stability and some semantic structure, but did not solve the annotation-quality gap.

Current conclusion:

- More prompt-only or model-size-only iteration is unlikely to be enough.
- The next useful step is to define owner-drawn GT annotations and evaluation summaries.
- Metric selection belongs to Phase 8.5 D, but full quantitative metrics require owner-drawn GT annotations from Phase 8.5 E.

Metric staging:

- Before manual GT: use weak summary metrics such as node count, edge count, relation type distribution, subtype coverage, uncertainty coverage, confidence distribution, schema validity, and repair count.
- After manual GT: add node precision/recall, relation predicate accuracy, subject-predicate-object triplet precision/recall, graph edit distance, and graph similarity.
